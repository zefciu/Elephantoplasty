from eplasty.ctx import get_cursor
from eplasty.column import BigSerial

class Table(object):
    """Parent class for all table classes"""
    
    def __init__(self, **kwargs):
        if not self.columns:
            raise NotImplementedError, 'Virtual class'
        
        col_names = [col.name for col in self.columns]
        for k, v in kwargs.iteritems():
            if k not in col_names:
                raise TypeError, 'Column {0} not in table {1}'.format(
                    k, self.name
                )
            setattr(self, k, v)
    
    def flush(self, cursor):
        """
Flush this object to database using given cursor
        """
        col_names = []
        col_values = []
        for col in self.columns:
            if hasattr(self, col.name):
                col_names.append(col.name)
                col_values.append(getattr(self, col.name))
        try:
            cursor.execute(
                'INSERT INTO {0} ({1}) VALUES ({2})'.format(
                    type(self).name, ', '.join(col_names),
                    ', '.join(['%s'] * len(col_names))
                ), 
                col_values
            )
        except Exception as e:
            raise # TODO
    
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
        
        
        
    