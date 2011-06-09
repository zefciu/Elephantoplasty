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
        
