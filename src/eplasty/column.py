from psycopg2.extensions import adapt


class Column(object):
    """Base class for all columns. Columns are descriptors."""
    __slots__ = ['name', 'pqtype', 'length', 'attrs']
    
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
        return "{name} {pqtype}{length} {attrs}".format(
            name = self.name,
            pqtype = self.pqtype,
            length = '({0})'.format(self.length) if self.length else '',
            attrs = ' '.join(self.attrs),
        )
        
    def bind_name(self, name):
        """Adds name to the column and returns self"""
        self.name = name
        return self
        
        
    
class BigSerial(Column):
    """PostgreSQL BigSerial type"""
    pqtype = 'bigserial'
    compat_types = [] #R/O
    
    
class Integer(Column):
    """PostgreSQL integer type"""
    pqtype = 'integer'
    compat_types = [int]
    
    
class CharacterVarying(Column):
    pqtype = 'character varying'
    compat_types = [basestring]
