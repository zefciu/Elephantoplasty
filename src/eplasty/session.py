from psycopg2 import ProgrammingError
from eplasty.util import queue_iterator
class Session(object):
    """
The sessions are orm wrappers of connections. They store the objects
and are able to flush them to database
    """
    
    def __init__(self, connection):
        self.connection = connection
        self.objects = []
        self.nopk_objects = {}
        self.pk_objects = {}
        
    def _rollback(self):
        """Rollback the connection and unset ``flushed`` flags"""
        self.connection.rollback()
        for o in self.objects:
            o._flushed = False
        
    def cursor(self, *args, **kwargs):
        return self.connection.cursor(*args, **kwargs)
    
    def add(self, o):
        self.objects.append(o)
        pk = o.get_pk_value()
        if pk:
            self.pk_objects.setdefault(type(o).__table_name__, {})
            self.pk_objects[type(o).__table_name__][pk] = o
        else:
            self.nopk_objects.setdefault(type(o).__table_name__, [])
            self.nopk_objects[type(o).__table_name__].append(o)
        
    def flush(self):
        from eplasty.table.const import NEW, MODIFIED, UPDATED, UNCHANGED
        cursor = self.cursor()
        queue = self.objects[:]
        for o in queue_iterator(queue):
            if o._status in [NEW, MODIFIED, UPDATED] and not o._flushed:
                if o._has_unflushed_dependencies():
                    queue.append(o)
                    continue
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
                o._flushed = False
                
        for tname, collection in self.nopk_objects.iteritems():
            self.pk_objects.setdefault(tname, {})
            for o in collection:
                self.pk_objects[tname][o.get_pk_value()] = o
            del collection[:]
            
    def find_cached(self, table_name, pk_value):
        try:
            return self.pk_objects[table_name][pk_value]
        except KeyError:
            return None
            
                    
        
    def commit(self):
        self.flush()
        self.connection.commit()
        
