class ResultIterator(object):
    def __init__(self, result):
        self.result = result
        self.cls = result.cls
        self.cursoriterator = iter(result.cursor)
    
    def next(self):
        tup = self.cursoriterator.next()
        if tup:
            return self.cls.hydrate(tup)
        else:
            raise StopIteration
        
        
        
class Result(object):
    """Wrapper around server-side cursor"""
    
    def __init__(self, cursor, cls):
        self.cursor = cursor
        self.cls = cls
        
    def __iter__(self):
        """Temporary solution I think"""
        return ResultIterator(self)
    
    
    def fetch(self, count):
        """Fetch ``count`` objects"""
        tuple_list = self.cursor.fetchmany(count)
        return [self.cls.hydrate(t) for t in tuple_list]