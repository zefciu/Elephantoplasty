'''
This module contains simple fields that only proxy a value from a single
'''

from base import Field
from eplasty import column as c

class Simple(Field):
    """Basic, abstract class for all simple fields"""

    ColumnType = None

    def __init__(self, name=None, *args, **kwargs):
        self.name = name
        self.column = self.ColumnType(name=name, *args, **kwargs)
        self.columns = [self.column]
        super(Simple, self).__init__(name, *args, **kwargs)

    def _get_value(self, inst, cls):
        return self.column._get_value(self, inst, cls)

    def get_c_vals(self, dict_):
        """Gets a mapping of column_name -> column_value for this field"""
        return {self.column.name: dict_[self.name]}

    def bind_class(self, cls, name):
        self.column.name = name
        return super(Simple, self).bind_class(cls, name)


class Integer(Simple):
    ColumnType = c.Integer

class CharacterVarying(Simple):
    ColumnType = c.CharacterVarying