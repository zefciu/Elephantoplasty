"""Base classes for columns"""
import abc
import datetime
from sys import version_info
from numbers import Integral

class Column(object, metaclass=abc.ABCMeta):
    """
    Columns are lower level than fields. They represent 1:1 the columns
    of underlying database table
    name: The postgres name for column
    pgtype: The postgres datatype
    length: The lengh option used with some datatypes
    unique: Whether to create a UNIQUE index
    """
    compat_types = []
    pgtype = None

    def __init__(
        self, name=None, length=None, null=True, default=False,
        references = None, unique=False
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
        self.unique = unique
        if unique:
            self.pgattrs.append(('UNIQUE', []))

        if default is not False:
            self.pgattrs.append(('DEFAULT %s', [default]))

        self.owner_class = None

    def render_full(self):
        """Returns the full, unambiguous name of this column that can be used
        in SQL."""
        return '{0}.{1}'.format(self.owner_class.__table_name__, self.name)

    @classmethod
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

class Character(Column):
    """PostgreSQL fixed character type"""
    pgtype = 'character varying'
    compat_types = [str]

class CharacterVarying(Column):
    """PostgreSQL character varying type"""
    pgtype = 'character varying'
    compat_types = [str]

class ByteA(Column):
    """PostgreSQL bytea typaracter varying"""
    pgtype = 'bytea'
    compat_types = [bytes]

class Text(Column):
    """PostgreSQL text type"""
    pgtype = 'text'
    compat_types = [str]

class DateTime(Column):
    """PostgreSQL datetime type"""
    pgtype = 'datetime'
    compat_types = [datetime.datetime]

class Date(Column):
    """PostgreSQL datetype"""
    pgtype = 'date'
    compat_types = [datetime.date]

class OID(Column):
    """PostgreSQL oid type"""
    pgtype = 'oid'
    compat_types = [Integral]

class Array(Column):
    """An array of other PostgreSQL type"""
    def __init__(self, *args, **kwargs):
        itemtype = kwargs.pop('itemtype').ColumnType
        self.itemtype = itemtype
        self.pgtype = itemtype.pgtype+'[]'
        super(Array, self).__init__(*args, **kwargs)

    def _is_compatible(self, value):
        return all([self.itemtype._is_compatible(item) for item in value])
