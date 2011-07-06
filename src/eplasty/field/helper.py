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

    def __init__(self, name=None, **kwargs):
        self.name = name
        self.columns = [BigSerial(name = name)]
        return super(SimplePK, self).__init__(name=name, **kwargs)
        
    def __set__(self, v, inst):
        raise AttributeError, 'Read only field'

    def __get__(self, inst, cls):
        return self.columns[0]._get_value(inst, cls)
    
    def sync_down(self):
        pass
