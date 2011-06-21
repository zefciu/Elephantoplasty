from base64 import b64encode
from hashlib import sha1
import itertools as it

from eplasty import conditions as cond
from eplasty.ctx import get_session
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
        
        col_names = [
            col.name for col in it.chain(self.columns, self.inh_columns)
        ]
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
    def _diff(self):
        r = []
        for c in self.columns:
            n = c.name
            if self._initial[n] != self._current[n]:
                r.append ((c, (self._initial[n], self._current[n])))
                
        return r
    
    def _flush_new(self, cursor):
        col_names = []
        col_values = []
        for col in it.chain(self.columns, self.inh_columns):
            if col.name in self._current:
                col_names.append(col.name)
                col_values.append(type(col).get_raw(self._current[col.name]))
        cursor.execute(
            'INSERT INTO {0} ({1}) VALUES ({2}) RETURNING {3}'.format(
                type(self).__table_name__, ', '.join(col_names),
                ', '.join(['%s'] * len(col_names)),
                type(self).pk
            ), 
            col_values
        )
        new_pk_val = cursor.fetchone()[0]
        self._current[type(self).pk] = new_pk_val
        self._initial = self._current.copy()
            
    def _flush_modified(self, cursor):
        diff = self._diff
        col_names = []
        col_values = []
        
        for col, (was, is_) in diff: #@UnusedVariable
            col_names.append('{0} = %s'.format(col.name))
            col_values.append(type(col).get_raw(is_))
            
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
    def _get_column_names(cls, all = False):
        """Returns column names as a comma separated string to be used in
        SQL queries"""
        columns = it.chain(cls.columns, cls.inh_columns) if all else cls.columns
        return ','.join((c.name for c in columns))
    
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
            dict_[col.name] = col.hydrate(v)
        
        self._initial = dict_.copy()
        self._current = dict_.copy()
        self._status = UNCHANGED
        self._flushed = False
            
        return self
    
    @classmethod
    def get_pk(cls):
        """Temporal solution before composite pk's are implemented"""
        for c in cls.columns:
            if c.name == cls.pk:
                return c
            
    def get_pk_value(self):
        """As above"""
        return self._current[self.pk]
    
    def _has_unflushed_dependencies(self):
        """Tells if there are some objects that should be flushed before this
        one"""
        result = []
        for c in self.columns:
            if c.name in self._current:
                for d in type(c).get_dependencies(self._current[c.name]):
                    if d._status == 'NEW' and not d._flushed:
                        result.append(d)
        return result or False
