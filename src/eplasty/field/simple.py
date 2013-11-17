'''
This module contains one-column read-write fields
'''

from .one_column import OneColumn
from eplasty import column as c

class Simple(OneColumn):
    """Basic, abstract class for all simple fields"""

    ColumnType = None

    def _is_compatible(self, v):
        return self.column._is_compatible(v)


class Integer(Simple):
    ColumnType = c.Integer

class CharacterVarying(Simple):
    ColumnType = c.CharacterVarying

class Character(Simple):
    ColumnType = c.Character

class ByteA(Simple):
    ColumnType = c.ByteA

    def process_col_val(self, col_val):
        return col_val.tobytes()

class Text(Simple):
    ColumnType = c.Text

class DateTime(Simple):
    ColumnType = c.DateTime

class Date(Simple):
    ColumnType = c.Date

class Array(Simple):
    def __init__(self, *args, **kwargs):
        self.itemtype = kwargs['itemtype']
        super(Array, self).__init__(*args, **kwargs)
    ColumnType = c.Array
