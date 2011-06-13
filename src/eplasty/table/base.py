from eplasty.ctx import get_cursor, get_session
from eplasty import conditions as cond
from eplasty.table.meta import TableMeta
from eplasty.table.exc import NotFound, TooManyFound
from eplasty.table.const import NEW, UNCHANGED

class Table(object):
    """Parent class for all table classes"""
    __metaclass__ = TableMeta
    
    def __init__(self, **kwargs):
        if not self.columns:
            raise NotImplementedError, 'Virtual class'
        
        col_names = [col.name for col in self.columns]
        self._current = dict()
        for k, v in kwargs.iteritems():
            if k not in col_names:
                raise TypeError, 'Column {0} not in table {1}'.format(
                    k, self.name
                )
            self._current[k] = v
            
        self._status = NEW
    
    def flush(self, cursor):
        """
Flush this object to database using given cursor
        """
        col_names = []
        col_values = []
        for col in self.columns:
            if col.name in self._current:
                col_names.append(col.name)
                col_values.append(self._current[col.name])
        try:
            cursor.execute(
                'INSERT INTO {0} ({1}) VALUES ({2})'.format(
                    type(self).name, ', '.join(col_names),
                    ', '.join(['%s'] * len(col_names))
                ), 
                col_values
            )
        except Exception as e:
            raise # TODO
    
    @classmethod
    def _get_column_names(cls):
        """Returns column names as a comma separated string to be used in
        SQL queries"""
        return ','.join((c.name for c in cls.columns))
    
    @classmethod
    def create_table(cls, ctx = None):
        cursor = get_cursor(ctx)
        column_decls = [c.declaration for c in cls.columns] 
        column_decls.append('CONSTRAINT id PRIMARY KEY (id)')
        command = """CREATE TABLE {tname}
        (
        {columns}
        );""".format(
            tname = cls.name, columns = ',\n'.join(column_decls)
        )
        
        cursor.execute(command)
        cursor.connection.commit()
        
    @classmethod
    def get(cls, id = None, session = None, *args, **kwargs):
        session = get_session(session)
        
        if id is not None:
            kwargs['id'] = id
        
        args = list(args)
        for k, v in kwargs.iteritems():
            args.append(cond.Equals(k, v))
            
        cursor = session.cursor()
        
        cond_string, cond_args = cond.And(*args).render()
        cursor.execute(
            'SELECT {col_names} FROM {tname} WHERE {conds}'.format(
                col_names = cls._get_column_names(),
                tname = cls.name,
                conds = cond_string,
            ),
            cond_args,
        )
        if cursor.rowcount == 1:
            r = cls.hydrate(cursor.fetchone())
            session.add(r)
            return r
        elif cursor.rowcount == 0:
            raise NotFound, "Didn't find anything"
        else:
            raise TooManyFound, "Found more than one row"
        
    @classmethod
    def hydrate(cls, tup):
        """Hydrates the object from given tuple"""
        self = cls.__new__(cls)
        dict_ = dict()
        for col, v in zip(cls.columns, tup):
            dict_[col.name] = v
        
        self._initial = dict_.copy()
        self._current = dict_.copy()
        self._status = UNCHANGED
            
        return self
