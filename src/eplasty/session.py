from eplasty.table.const import NEW, MODIFIED, UPDATED
class Session(object):
    """
The sessions are orm wrappers of connections. They store the objects
and are able to flush them to database
    """
    
    def __init__(self, connection):
        self.connection = connection
        # self.cursors = []
        self.objects = []
        
    def cursor(self):
        return self.connection.cursor()
    
    def add(self, o):
        self.objects.append(o)
        
    def flush(self):
        cursor = self.cursor()
        for o in self.objects:
            if o._status in [NEW, MODIFIED, UPDATED]:
                o.flush(cursor)
        
    def commit(self):
        self.flush()
        self.connection.commit()
        
