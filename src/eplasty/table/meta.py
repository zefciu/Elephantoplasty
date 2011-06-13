from eplasty.column import BigSerial, Column
class TableMeta(type):
    """Metaclass for table types"""
    
    def __init__(cls, classname, bases, dict_):
        columns = [
            c.bind_name(n)
            for n, c in dict_.iteritems() if isinstance(c, Column)
        ]
        
        if not columns:
            cls.abstract = True
        else:
            if 'pk' not in dict_:
                columns.insert(0, BigSerial('id'))
                dict_['pk'] = ('id')
                
            cls.pk = dict_['pk']
            cls.columns = columns
            
            dict_.pop('pk', None)
        
        super(TableMeta, cls).__init__(classname, bases, dict_)
