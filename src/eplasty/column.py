from psycopg2.extensions import adapt

class Column(object):
    """
    Columns are lower level than fields. They represent 1:1 the columns
    of underlying database table
    """
    __slots__ = [
        'name', 'pgtype', 'length', 'attrs', 'owner_class',
        'owner', 'pseudo', 'compat_types'
    ]

    pseudo = False

    def __init__(
        self, name=None, length=None, null=True, default=False,
        references = None, **kwargs
    ):
        self.name = name
        self.length = length
        self.null = null
        self.default = default
        self.references = references

        self.pgattrs = []

        if not null:
            self.pgattrs.append(('NOT NULL', []))
        else:
            self.compat_types.append(type(None))

        if default is not False:
            self.pgattrs.append(('DEFAULT %s', [default]))

        self.owner_class = None

    def _is_compatible(self, v):
        """Checks if python variable is compatible with this column."""
        for t in self.compat_types:
            if isinstance(v, t):
                return True
        return False

    def _set_value(self, v, inst, cls):
        from eplasty.object.const import MODIFIED, UNCHANGED, UPDATED
        if not self._is_compatible(v):
            raise TypeError(('Python type {0} is not compatible with column'
                'type {1}').format(type(v), type(self)))
        inst._current[self.name] = v
        if inst._status in [UNCHANGED, UPDATED]:
            inst._status = MODIFIED
        
    def _get_value(self, inst, cls):
        return inst._current[self.name]

    @property
    def declaration(self):
        if self.pseudo:
            return None
        return "{name} {pgtype}{length} {pgattrs}".format(
            name = self.name,
            pgtype = self.pgtype,
            length = '({0})'.format(self.length) if self.length else '',
            pgattrs = ' '.join(a[0] for a in self.pgattrs),
        ), sum([a[1] for a in self.pgattrs], [])

    def bind(self, cls, name):
        """Adds owner class and name to the column and returns self"""
        self.owner_class = cls
        self.name = name
        return self

    def hydrate(self, value, session):
        """Transform raw value from database to object version"""
        return value

    def get_raw(self, value):
        """Get the value as it will appear in the database
        """
        return self.__get__(self.owner, type(self.owner))

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

class BigInt(Column):
    """PostgreSQL integer type"""
    pgtype = 'bigint'
    compat_types = [int]


class CharacterVarying(Column):
    pgtype = 'character varying'
    compat_types = [str]
