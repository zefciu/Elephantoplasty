'''
Various useful field types
'''

from base import Field
from eplasty.column import BigSerial

class SimplePK(Field):
    """
    Simple artificial integer primary key with sequential values. Used as
    default if no other primary key is specified.
    """

    def __init__(self, name):
        self.name = name
        self.columns = [BigSerial(name = name)]
        
    def __set__(self, v, inst):
        raise AttributeError, 'Read only field'

    def __get__(self, inst, cls):
        return self.columns[0]._get_value(inst, cls)
