"""OneColumn definition"""
from abc import ABCMeta
from .base import Field

class OneColumn(Field):
    __metaclass__ = ABCMeta
    '''
    Base class for all field that just proxy one column
    '''

    def __init__(self, name=None, *args, **kwargs):
        self.name = name
        self.column = self.ColumnType(name=name, *args, **kwargs)
        self.columns = [self.column]
        super(OneColumn, self).__init__(name, *args, **kwargs)


    def get_c_vals(self, dict_):
        """Gets a mapping of column_name -> column_value for this field"""
        if self.name in dict_:
            return {self.column.name: dict_[self.name]}
        else:
            return {}

    def bind_class(self, cls, name):
        self.column.name = name
        return super(OneColumn, self).bind_class(cls, name)

    def hydrate(self, inst, col_vals, dict_, session):
        dict_[self.name] = col_vals[self.column.name]
        

