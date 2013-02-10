from base64 import b64encode
from hashlib import sha1
import itertools as it

from psycopg2 import ProgrammingError
from psycopg2.errorcodes import UNDEFINED_TABLE

from eplasty.ctx import get_session
from eplasty.result import Result
from eplasty.lazy import LazyQuery

from eplasty.object.meta import ObjectMeta
from eplasty.object.exc import NotFound, TooManyFound
from eplasty.object.const import (
    NEW, MODIFIED, ORPHANED, DELETED, UPDATED, UNCHANGED
)
from eplasty.util import prepare_col
from eplasty.query import SelectQuery

class Object(object, metaclass=ObjectMeta):
    """Parent class for all eplasty Object classes"""

    
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
        self.session = None
        self.temporary = []
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
                col_names.append('"{0}"'.format(cname))
                col_values.append(cval)
        # print cursor.mogrify(
        #     'INSERT INTO {0} ({1}) VALUES ({2}) RETURNING {3}'.format(
        #         type(self).__table_name__, ', '.join(col_names),
        #         ', '.join(['%s'] * len(col_names)),
        #         ','.join(type(self).__pk__)
        #     ), 
        #     col_values
        # )
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
            for c, v in cvals.items():
                col_names.append('"{0}" = %s'.format(c))
                col_values.append(v)

        if not col_names: #Might happend when modified field has no columns
            return
            
        pk = self._current['id']
        col_names = ', '.join(col_names)
        
        cursor.execute(
            'UPDATE {0} SET {1} WHERE id = %s'.format(
                self.__table_name__, col_names
            ), col_values + [pk]
        )
        
    def _do_delete(self, session, cursor):
        """Performs the actual deletion from database"""
        #for field in self.fields:
        #    if field.before_delete is not None:
        #        field.before_delete(self, session, cursor)
        cursor.execute(
            'DELETE FROM {0} WHERE {1} = %s'.format(
                self.__table_name__,
                prepare_col(type(self).get_pk()),
            ),
            [self.get_pk_value()],
        )
        for field in self.fields:
            if field.after_delete is not None:
                field.after_delete(self, session, cursor)

    def set_orphan_status(self):
        """Sets the status to ORPHANED if it makes sense"""
        if self._status != DELETED:
            self._status = ORPHANED

    def check_orphan_status(self):
        """Checks if the object is still an orphan and deletes the orphan status
        appropriately"""
        for f in self.fields:
            if f.orphaned:
                self.set_orphan_status()
                return
        if self._status == ORPHANED:
            self._status = MODIFIED

    def delete(self):
        """Marks this object as deleted"""
        self._status = DELETED

    def flush(self, session, cursor):
        """
Flush this object to database using given cursor
        """
        if self._status == NEW:
            self._flush_new(session, cursor)
        elif self._status == MODIFIED:
            self._flush_modified(session, cursor)
        elif self._status in [DELETED, ORPHANED]:
            self._do_delete(session, cursor)
        
    @classmethod
    def _get_conditions(cls, *args, **kwargs):
        """Reformats args and kwargs to a ``Condition`` object"""
        from eplasty import conditions as cond
        args = list(args)
        # for k, v in kwargs.items():
        #     args.append(cond.Equals(k, v))
        
        if not args:
            return cond.All()
            
        return cond.And(*args)
    
    @classmethod
    def _get_query(
        cls, condition, order, fields=None, limit=None, offset=None
    ):
        """Returns tuple to be executed for this class and given
        ``condition``"""
        fields = fields or [field.name for field in cls.fields if field.cheap]

        columns = sum((getattr(cls, field).columns for field in fields), [])
        return SelectQuery(
            cls.__table_name__, columns = columns, condition = condition,
            order = order, limit=limit, offset=offset,
        ).render(), fields
        
    @classmethod
    def get(cls, id = None, session = None, fields = None, *args, **kwargs):
        if fields:
            import pdb; pdb.set_trace()
        from eplasty import conditions as cond
        args = list(args)
        session = get_session(session)
        cached =  session.find_cached(cls.__table_name__, id)
        if cached:
            return cached
        if isinstance(id, cond.Condition):
            args.append(id)
        elif id is not None:
            args.append(cond.Equals(cls.get_pk(), id)) 
        
            
        cursor = session.cursor()
        
        condition = cls._get_conditions(*args, **kwargs)
        order = kwargs.get('order', [])
        query, fields = cls._get_query(condition, order, fields)
        try:
            cursor.execute(*query)
        except ProgrammingError as err:
            if err.pgcode == UNDEFINED_TABLE:
                session._rollback(True)
                raise NotFound("Didn't find anything")
            else:
                raise

        
        if cursor.rowcount == 1:
            r = cls.hydrate(cursor.fetchone(), session, fields = fields)
            session.add(r)
            return r
        elif cursor.rowcount == 0:
            raise NotFound("Didn't find anything")
        else:
            raise TooManyFound("Found more than one row")
    
    @classmethod
    def find(cls, *args, **kwargs):
        """
        Execute the query on this object class and return a ``Result`` object.
        """
        s = kwargs.pop('session', None)
        session = get_session(s)
        tmp_cursor = session.cursor()
        condition = cls._get_conditions(*args, **kwargs)
        
        order = kwargs.pop('order', [])
        fields = kwargs.pop('fields', None)
        limit = kwargs.pop('limit', None)
        offset = kwargs.pop('offset', None)
        query, fields = cls._get_query(condition, order, fields, limit, offset)
        query_hash = b64encode(sha1(tmp_cursor.mogrify(*query)).digest())
        cursor = session.cursor()
        try:
            cursor.execute(*query)
        except ProgrammingError as err:
            if err.pgcode == UNDEFINED_TABLE:
                session._rollback(True)
                return []
            else:
                raise
        
        return Result(session, cursor, cls, fields)

    def _load_field(self, field):
        """Load a field that wasn't fetched while object was loaded."""
        from eplasty import conditions as cond
        condition = cond.Equals(type(self).get_pk(), self.get_pk_value()) 
        query, fields = self._get_query(condition, order = [], fields = [field.name])
        cursor = self.session.cursor()
        cursor.execute(*query)
        row = cursor.fetchall()[0]
        col_vals = {}
        for col, col_val in zip(field.columns, row):
            col_vals[col.name] = col.hydrate(col_val, self.session)
        self.field_map[field.name].hydrate(
            self, col_vals, self._current, self.session
        )
        


        
    
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
            for d in f.get_dependencies(self._current):
                if (
                    not isinstance(d, LazyQuery) and
                    (d._status == NEW and not d._flushed)
                ):
                    result.append(d)
        return result or False

    def bind_session(self, session):
        """Sets the current session"""
        self.session = session
        for f in self.fields:
            f.bind_session(self, session)
        session.add(*self.temporary)
        self.temporary = []

    def add(self, *os):
        """Adds an object to this object's session or to a temporary storage
        (to be added when adding this one"""
        if self.session is not None:
            self.session.add(*os)
        else:
            self.temporary += os

    def touch(self):
        """Set status to modified if applicable"""
        if self._status in [UNCHANGED, UPDATED]:
            self._status = MODIFIED

