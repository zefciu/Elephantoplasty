class Column(object):
    """Base class for all columns"""
    __slots__ = ['name', 'pqtype', 'length', 'attrs']
    
    def __init__(self, name, length = None, attrs = None):
        self.name = name
        self.length = length
        self.attrs = attrs or []
    
    def check_compatibility(self, v):
        """Checks if python variable is compatible with this column."""
        for t in self.compat_types:
            if isinstance(v, t):
                return True
        return False
    
    @property
    def declaration(self):
        return "{name} {pqtype}{length} {attrs}".format(
            name = self.name,
            pqtype = self.pqtype,
            length = '({0})'.format(self.length) if self.length else '',
            attrs = ' '.join(self.attrs),
        )
        
    
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
