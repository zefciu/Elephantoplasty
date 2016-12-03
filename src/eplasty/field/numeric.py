from eplasty import column
from eplasty.field.base import SingleColumnField


class Integer(SingleColumnField):
    """Int field"""

    ColumnType = column.Integer
