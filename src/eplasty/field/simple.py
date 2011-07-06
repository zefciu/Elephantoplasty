'''
This module contains simple fields that only proxy a value from a single
'''

from base import Field
from eplasty import column as c

class Simple(Field):

    ColumnType = None

    def __init__(self, *args, **kwargs):
        self.column = self.ColumnType(name = self.name, *args, **kwargs)
        self.columns = [self.column]

    def _get_value(self, inst, cls):
        return self.column._get_value(self, inst, cls)

    def sync_down(self):
        self.columns._set_value(self, self._value, self.owner, self.owner_class)


class Integer(Simple):
    ColumnType = c.Integer

class CharacterVarying(Simple):
    ColumnType = c.CharacterVarying