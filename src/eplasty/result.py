class ResultIterator(object):
    def __init__(self, result):
        self.result = result
        self.cls = result.cls
        self.cursoriterator = iter(result.cursor)
    
    def next(self):
        tup = self.cursoriterator.next()
        return self.cls.hydrate(tup, self.result.session)
        
        
class Result(object):
    """Wrapper around server-side cursor"""
    
    def __init__(self, session, cursor, cls):
        self.session = session
        self.cursor = cursor
        self.cls = cls
        
    def __iter__(self):
        """Temporary solution I think"""
        return ResultIterator(self)
    
    def fetch(self, count):
        """Fetch ``count`` objects"""
        tuple_list = self.cursor.fetchmany(count)
        return [self.cls.hydrate(t, self.session) for t in tuple_list]