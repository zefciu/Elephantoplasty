from eplasty import column
from eplasty.field.base import SingleColumnField


class Char(SingleColumnField):
    """VarChar field"""

    ColumnType = column.VarChar
