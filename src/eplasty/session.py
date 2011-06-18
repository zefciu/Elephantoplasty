from psycopg2 import ProgrammingError
class Session(object):
    """
The sessions are orm wrappers of connections. They store the objects
and are able to flush them to database
    """
    
    def __init__(self, connection):
        self.connection = connection
        # self.cursors = []
        self.objects = []
        
    def _rollback(self):
        """Rollback the connection and unset ``flushed`` flags"""
        self.connection.rollback()
        for o in self.objects:
            o._flushed = False
        
    def cursor(self, *args, **kwargs):
        return self.connection.cursor(*args, **kwargs)
    
    def add(self, o):
        self.objects.append(o)
        
    def flush(self):
        from eplasty.table.const import NEW, MODIFIED, UPDATED, UNCHANGED
        cursor = self.cursor()
        for o in self.objects:
            if o._status in [NEW, MODIFIED, UPDATED] and not o._flushed:
                try:
                    o.flush(cursor)
                    o._flushed = True
                except ProgrammingError as e:
                    if e.pgcode == '42P01': # Table doesn't exist
                        cursor.connection.commit()
                        type(o).create_table(cursor)
                        self._rollback()
                        self.flush()
                        return
                    else:
                        raise
                    
        self.connection.commit()
        for o in self.objects:
            if o._flushed:
                o._status = UNCHANGED
            
                    
        
    def commit(self):
        self.flush()
        self.connection.commit()
        
