from base64 import b64encode
from hashlib import sha1

from eplasty.ctx import get_cursor, get_session
from eplasty import conditions as cond
from eplasty.table.meta import TableMeta
from eplasty.table.exc import NotFound, TooManyFound
from eplasty.table.const import NEW, UNCHANGED, MODIFIED
from eplasty.result import Result

class Table(object):
    """Parent class for all table classes"""
    __metaclass__ = TableMeta
    
    def __init__(self, **kwargs):
        if self._abstract:
            raise NotImplementedError, 'Abstract class'
        
        col_names = [col.name for col in self.columns]
        self._current = dict()
        for k, v in kwargs.iteritems():
            if k not in col_names:
                raise TypeError, 'Class {0} has no attribute {1}'.format(
                    type(self).__name__, k
                )
            self._current[k] = v
            
        self._status = NEW
        self._flushed = False
        
    @property
    def diff(self):
        r = {}
        for c in self.columns:
            n = c.name
            if self._initial[n] != self._current[n]:
                r[n] = (self._initial[n], self._current[n])
                
        return r
    
    def _flush_new(self, cursor):
        col_names = []
        col_values = []
        for col in self.columns:
            if col.name in self._current:
                col_names.append(col.name)
                col_values.append(self._current[col.name])
        cursor.execute(
            'INSERT INTO {0} ({1}) VALUES ({2})'.format(
                type(self).__table_name__, ', '.join(col_names),
                ', '.join(['%s'] * len(col_names))
            ), 
            col_values
        )
            
    def _flush_modified(self, cursor):
        diff = self.diff
        col_names = []
        col_values = []
        
        for k, v in diff.iteritems():
            was, is_ = v #@UnusedVariable
            col_names.append('{0} = %s'.format(k))
            col_values.append(is_)
            
        pk = self._current['id']
        col_names = ', '.join(col_names)
        
        cursor.execute(
            'UPDATE {0} SET {1} WHERE id = %s'.format(
                self.__table_name__, col_names
            ), col_values + [pk]
        )
    
    def flush(self, cursor):
        """
Flush this object to database using given cursor
        """
        if self._status == NEW:
            self._flush_new(cursor)
        elif self._status == MODIFIED:
            self._flush_modified(cursor)
            
    
    @classmethod
    def _get_column_names(cls):
        """Returns column names as a comma separated string to be used in
        SQL queries"""
        return ','.join((c.name for c in cls.columns))
    
    @classmethod
    def _get_conditions(cls, *args, **kwargs):
        """Reformats args and kwargs to a ``Condition`` object"""
        args = list(args)
        for k, v in kwargs.iteritems():
            args.append(cond.Equals(k, v))
        
        if not args:
            return cond.All()
            
        return cond.And(*args)
    
    @classmethod
    def _get_query(cls, condition):
        """Returns tuple to be executed for this class and given
        ``condition``"""
        cond_string, cond_args = condition.render()
        return(
            'SELECT {col_names} FROM {tname} WHERE {conds}'.format(
                col_names = cls._get_column_names(),
                tname = cls.__table_name__,
                conds = cond_string,
            ),
            cond_args,
        )
        
    
    @classmethod
    def create_table(cls, ctx = None):
        cursor = get_cursor(ctx)
        column_decls = [c.declaration for c in cls.columns] 
        column_decls.append('PRIMARY KEY (id)')
        command = """CREATE TABLE {tname}
        (
        {columns}
        );""".format(
            tname = cls.__table_name__, columns = ',\n'.join(column_decls)
        )
        
        cursor.execute(command)
        cursor.connection.commit()
        
    @classmethod
    def get(cls, id = None, session = None, *args, **kwargs):
        session = get_session(session)
        
        if id is not None:
            kwargs['id'] = id
        
            
        cursor = session.cursor()
        
        condition = cls._get_conditions(*args, **kwargs)
        cursor.execute(*cls._get_query(condition))
        
        if cursor.rowcount == 1:
            r = cls.hydrate(cursor.fetchone())
            session.add(r)
            return r
        elif cursor.rowcount == 0:
            raise NotFound, "Didn't find anything"
        else:
            raise TooManyFound, "Found more than one row"
    
    @classmethod
    def find(cls, session = None, *args, **kwargs):
        """Execute the query on this table and return a ``Result`` object."""
        session = get_session(session)
        tmp_cursor = session.cursor()
        condition = cls._get_conditions(*args, **kwargs)
        
        query = cls._get_query(condition)
        query_hash = b64encode(sha1(tmp_cursor.mogrify(*query)).digest())
        cursor = session.cursor(query_hash)
        cursor.execute(*query)
        
        return Result(cursor, cls)
        
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
        self._flushed = False
            
        return self