'''
Helper objects for lazy object loading
'''

class LazyQuery(object):
    """This object stores a deferred ``get()`` of ``find()`` operation.
    It replaces the actual object in related objects cache. Call it to return
    the object or results."""
    
    def __init__(self, cls, fun, *args, **kwargs):
        self.cls = cls
        self.fun = fun
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return getattr(self.cls, self.fun)(*self.args, **self.kwargs)