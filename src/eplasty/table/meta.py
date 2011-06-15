from eplasty.column import BigSerial, Column
from eplasty.util import clsname2tname

class TableMeta(type):
    """Metaclass for table types"""
    
    def __init__(cls, classname, bases, dict_):
        columns = [
            c.bind_name(n)
            for n, c in dict_.iteritems() if isinstance(c, Column)
        ]
        
        if not columns:
            cls._abstract = True
        else:
            cls._abstract = False
            cls._setup_non_abstract(classname, bases, dict_, columns)
        
        super(TableMeta, cls).__init__(classname, bases, dict_)
        
    def _setup_non_abstract(cls, classname, bases, dict_, columns): #@NoSelf
        """Setups the non-abstract class creating primary key if needed and
selecting a table name"""

        if 'pk' not in dict_:
            columns.insert(0, BigSerial('id'))
            dict_['pk'] = ('id')
            
        cls.pk = dict_['pk']
        cls.columns = columns
         
        dict_.pop('pk', None)
        
        if '__table_name__' in dict_:
            cls.__table_name__ = dict_['__table_name__']
        else:
            cls.__table_name__ = clsname2tname(classname)
            
        dict_.pop('__table_name__', None)
        
        
