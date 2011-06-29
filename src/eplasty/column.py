from psycopg2.extensions import adapt


class Column(object):
    """Base class for all columns. Columns are descriptors."""
    __slots__ = ['name', 'pgtype', 'length', 'attrs', 'constraint']
    
    constraint = None
    
    def __init__(self, name = None, length = None, null= True, default = False):
        self.name = name
        self.length = length
        self.null = null
        self.default = default
        
        self.attrs = []
        
        if not null:
            self.attrs.append('NOT NULL')
        if default is not False:
            self.attrs.append('DEFAULT {0}'.format(adapt(default).getquoted()))
    
    def _is_compatible(self, v):
        """Checks if python variable is compatible with this column."""
        for t in self.compat_types:
            if isinstance(v, t):
                return True
        return False
    
    def __set__(self, inst, v):
        from eplasty.table.const import MODIFIED, UNCHANGED, UPDATED
        if not self._is_compatible(v):
            raise TypeError, ('Python type {0} is not compatible with column'
                'type {1}').format(type(v), type(self))
        inst._current[self.name] = v
        if inst._status in [UNCHANGED, UPDATED]:
            inst._status = MODIFIED
        
    def __get__(self, inst, cls):
        return inst._current[self.name]
    
    @property
    def declaration(self):
        return "{name} {pgtype}{length} {attrs}".format(
            name = self.name,
            pgtype = self.pgtype,
            length = '({0})'.format(self.length) if self.length else '',
            attrs = ' '.join(self.attrs),
        )
        
    def bind(self, cls, name):
        """Adds owner class and name to the column and returns self"""
        self.owner_class = cls
        self.name = name
        return self
    
    def hydrate(self, value):
        """Transform raw value from database to object version"""
        return value
    
    @classmethod
    def get_raw(cls, value):
        """Get the value as it will appear in the database
        """
        return value
    
    @classmethod
    def get_dependencies(self, value):
        """Get a list of objects that should be flushed before this one"""
        return []
    
        
        
    
class BigSerial(Column):
    """PostgreSQL BigSerial type"""
    pgtype = 'bigserial'
    compat_types = [] #R/O
    
    
class Integer(Column):
    """PostgreSQL integer type"""
    pgtype = 'integer'
    compat_types = [int]
    
    
class CharacterVarying(Column):
    pgtype = 'character varying'
    compat_types = [basestring]
