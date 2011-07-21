from base64 import b64encode
from hashlib import sha1
import itertools as it

from eplasty import conditions as cond
from eplasty.ctx import get_session
from eplasty.result import Result

from .meta import ObjectMeta
from .exc import NotFound, TooManyFound
from .const import NEW, MODIFIED

class Object(object):
    """Parent class for all eplasty Object classes"""
    __metaclass__ = ObjectMeta
    
    def __init__(self, **kwargs):
        if self._abstract:
            raise NotImplementedError('Abstract class')
        
        
        field_names = [
            field.name for field in it.chain(self.fields, self.inh_fields)
        ]
        self._status = NEW
        self._flushed = False
        for k, v in kwargs.items():
            if k not in field_names:
                raise TypeError('Class {0} has no attribute {1}'.format(
                    type(self).__name__, k
                ))
            setattr(self, k, v)
            
    def __new__(cls, *args, **kwargs):
        self = super(Object, cls).__new__(cls)
        self._current = {}
        self._initial = {}
        return self

    @property
    def _diff(self):
        r = []
        for f in self.fields:
            n = f.name
            if self._initial[n] != self._current[n]:
                r.append ((f, (self._initial[n], self._current[n])))
        return r

    def _flush_new(self, session, cursor):
        col_names = []
        col_values = []
        for f in it.chain(self.fields, self.inh_fields):
            cvals = f.get_c_vals(self._current)
            for cname, cval in cvals.items():
                col_names.append(cname)
                col_values.append(cval)
        cursor.execute(
            'INSERT INTO {0} ({1}) VALUES ({2}) RETURNING {3}'.format(
                type(self).__table_name__, ', '.join(col_names),
                ', '.join(['%s'] * len(col_names)),
                ','.join(type(self).__pk__)
            ), 
            col_values
        )
        new_pk_val = cursor.fetchone()
        for pk_val in zip(self.__pk__, new_pk_val):
            col, val = pk_val
            self._current[col] = val
            
        self._initial = self._current.copy()
            
    def _flush_modified(self, session, cursor):
        diff = self._diff
        col_names = []
        col_values = []
        
        for f, (was, is_) in diff: #@UnusedVariable
            cvals = f.get_c_vals(self._current)
            for c, v in cvals.iteritems():
                col_names.append('{0} = %s'.format(c))
                col_values.append(v)
            
        pk = self._current['id']
        col_names = ', '.join(col_names)
        
        cursor.execute(
            'UPDATE {0} SET {1} WHERE id = %s'.format(
                self.__table_name__, col_names
            ), col_values + [pk]
        )
    
    def flush(self, session, cursor):
        """
Flush this object to database using given cursor
        """
        if self._status == NEW:
            self._flush_new(session, cursor)
        elif self._status == MODIFIED:
            self._flush_modified(session, cursor)
            
    
    @classmethod
    def _get_column_names(cls, all = False):
        """Returns column names as a comma separated string to be used in
        SQL queries"""
        columns = it.chain(cls.columns, cls.inh_columns) if all else cls.columns
        return ','.join((c.name for c in columns if not c.pseudo))
    
    @classmethod
    def _get_conditions(cls, *args, **kwargs):
        """Reformats args and kwargs to a ``Condition`` object"""
        args = list(args)
        for k, v in kwargs.items():
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
        cached =  session.find_cached(cls.__table_name__, id)
        if cached:
            return cached
        
        if id is not None:
            kwargs['id'] = id
        
            
        cursor = session.cursor()
        
        condition = cls._get_conditions(*args, **kwargs)
        cursor.execute(*cls._get_query(condition))
        
        if cursor.rowcount == 1:
            r = cls.hydrate(cursor.fetchone(), session)
            session.add(r)
            return r
        elif cursor.rowcount == 0:
            raise NotFound("Didn't find anything")
        else:
            raise TooManyFound("Found more than one row")
    
    @classmethod
    def find(cls, session = None, *args, **kwargs):
        """
        Execute the query on this object class and return a ``Result`` object.
        """
        session = get_session(session)
        tmp_cursor = session.cursor()
        condition = cls._get_conditions(*args, **kwargs)
        
        query = cls._get_query(condition)
        query_hash = b64encode(sha1(tmp_cursor.mogrify(*query)).digest())
        cursor = session.cursor()
        cursor.execute(*query)
        
        return Result(session, cursor, cls)
        
    
    @classmethod
    def get_pk(cls):
        """Get the tuple of columns acting as pk"""
        return tuple((c for c in cls.columns if c.name in cls.__pk__))
            
    def get_pk_value(self):
        """Get the tuple of values for the pk or None"""
        try:
            return tuple((self._current[k] for k in type(self).__pk__))
        except KeyError:
            return None
    
    def _has_unflushed_dependencies(self):
        """Tells if there are some objects that should be flushed before this
        one"""
        result = []
        for f in self.fields:
#           if f.name in self._current:
            for d in f.get_dependencies(self._current):
                if d._status == NEW and not d._flushed:
                    result.append(d)
        return result or False
