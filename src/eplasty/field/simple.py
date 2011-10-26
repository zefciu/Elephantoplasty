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
