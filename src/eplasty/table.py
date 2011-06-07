from eplasty.ctx import get_cursor
from eplasty.column import BigSerial

class Table(object):
    """Parent class for all table classes"""
    
    @classmethod
    def _get_column_names(cls):
        """Returns column names as a comma separated string to be used in
        SQL queries"""
        return ','.join((c.name for c in cls.columns))
    
    @classmethod
    def create_table(cls, ctx = None):
        cursor = get_cursor(ctx)
        cls.columns.insert(0, BigSerial('id'))
        column_decls = [c.declaration for c in cls.columns] 
        column_decls.append('CONSTRAINT id PRIMARY KEY (id)')
        command = """CREATE TABLE {tname}
        (
        {columns}
        );""".format(
            tname = cls.name, columns = ',\n'.join(column_decls)
        )
        
        cursor.execute(command)
        cursor.connection.commit()
        
        
        
    