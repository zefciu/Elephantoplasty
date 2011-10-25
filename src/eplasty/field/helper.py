'''
Various useful field types
'''

from .one_column import OneColumn
from eplasty.column import BigSerial

class SimplePK(OneColumn):
    """
    Simple artificial integer primary key with sequential values. Used as
    default if no other primary key is specified.
    """

    RO_MESSAGE = "PK's are read-only"
    ColumnType = BigSerial

    def __init__(self, name=None, **kwargs):
        self.name = name
        self.columns = [BigSerial(name = name)]
        return super(SimplePK, self).__init__(name=name, **kwargs)

    def _is_compatible(self, value):
        raise NotImplementedError
