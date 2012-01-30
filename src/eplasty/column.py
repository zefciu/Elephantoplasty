"""Base classes for columns"""
import abc

class Column(object):
    """
    Columns are lower level than fields. They represent 1:1 the columns
    of underlying database table
    """
    __metaclass__ = abc.ABCMeta
    __slots__ = [
        'name', 'pgtype', 'length', 'attrs', 'owner_class',
        'owner'
    ]
    compat_types = []
    pgtype = None

    def __init__(
        self, name=None, length=None, null=True, default=False,
        references = None
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

    def render_full(self):
        """Returns the full, unambiguous name of this column that can be used
        in SQL."""
        return '{0}.{1}'.format(self.owner_class.__table_name__, self.name)

    def _is_compatible(self, value):
        """Checks if python variable is compatible with this column."""
        for type_ in self.compat_types:
            if isinstance(value, type_):
                return True
        return False

    @property
    def declaration(self):
        """The declaration for this column used for CREATE"""
        return '"{name}" {pgtype}{length} {pgattrs}'.format(
            name = self.name,
            pgtype = self.pgtype,
            length = '({0})'.format(self.length) if self.length else '',
            pgattrs = ' '.join(a[0] for a in self.pgattrs),
        ), sum([a[1] for a in self.pgattrs], [])


    def bind(self, cls):
        """Adds owner class and name to the column and returns self"""
        self.owner_class = cls
        return self

    def hydrate(self, value, session):
        """Transform raw value from database to object version"""
        return value


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
    """PostgreSQL character varying type"""
    pgtype = 'character varying'
    compat_types = [str]

class OID(Column):
    """PostgreSQL oid type"""
    pgtype = 'oid'
    compat_types = [int, long]
