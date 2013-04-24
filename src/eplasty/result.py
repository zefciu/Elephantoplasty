"""Results are iterable lazy wrappers around server-side cursor"""

class ResultIterator(object):
    """The iterator for Result"""
    def __init__(self, result):
        self.result = result
        self.cls = result.cls
        self.cursoriterator = iter(result.cursor)
    
    def __next__(self):
        tup = next(self.cursoriterator)
        new_object =  self.cls.hydrate(
            tup, self.result.session, self.result.fields
        )
        self.result.session.add(new_object)
        return new_object
        
        
class Result(object):
    """Wrapper around server-side cursor"""
    
    def __init__(self, session, cursor, cls, fields):
        self.session = session
        self.cursor = cursor
        self.cls = cls
        self.fields = fields
        
    def __iter__(self):
        """Temporary solution I think"""
        return ResultIterator(self)

    def fetch(self, count):
        """Fetch ``count`` objects"""
        tuple_list = self.cursor.fetchmany(count)
        return [
            self.cls.hydrate(t, self.session, self.fields) for t in tuple_list
        ]
