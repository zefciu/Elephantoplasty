from eplasty.column import BigSerial, Column
from eplasty.util import clsname2tname
from eplasty.ctx import get_cursor

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

        cls.parent_classes = [b for b in bases if not b._abstract]
        cls.inh_columns = sum([
            p_cls.columns for p_cls in cls.parent_classes
        ], [])
            
        if '__pk__' not in dict_:
            if cls.parent_classes: 
                dict_['__pk__'] = cls.parent_classes[0].__pk__
            else:
                columns.insert(0, BigSerial('id'))
                dict_['__pk__'] = 'id'
            
        cls.__pk__ = dict_['__pk__']
        dict_.pop('__pk__', None)
            
        cls.columns = columns
        
        if '__table_name__' in dict_:
            cls.__table_name__ = dict_['__table_name__']
        else:
            cls.__table_name__ = clsname2tname(classname)
            
        dict_.pop('__table_name__', None)

    def create_table(cls, ctx = None): #@NoSelf
        cursor = get_cursor(ctx)
        column_decls = []
        constraints = []
        for c in cls.columns:
            column_decls.append(c.declaration) 
            if c.constraint:
                constraints.append(c.constraint)
        constraints.append('PRIMARY KEY (id)')
        command = """CREATE TABLE {tname}
        (
        {columns}
        )
        {inh_clause};""".format(
            tname = cls.__table_name__, columns = ',\n'.join(
                column_decls + constraints
            ), inh_clause = (
                'INHERITS ({0})'.format(', '.join((
                    c.__table_name__ for c in cls.parent_classes)
                )) if cls.parent_classes else ''
            )
        )
        
        cursor.execute(command)
        cursor.connection.commit()
