import itertools as it

class Condition(object):
    """Base class for conditions"""
    def render(self):
        raise NotImplementedError
    
class All():
    """Get all rows"""
    def render(self):
        return '1 = 1', tuple()
    
class Equals(Condition):
    """Simple equality condition"""
    def __init__(self, col_name, value):
        self.col_name = col_name
        self.value = value
        
    def render(self):
        return '{0} = %s'.format(self.col_name), (self.value,)

class And(Condition):
    """Logical AND of several conditions"""
    def __init__(self, *args):
        self.args = args
        
    def render(self):
        strings = (c.render()[0] for c in self.args)
        fmt_args = it.chain(*(c.render()[1] for c in self.args))
        
        return (
            ' AND '.join(('({0})'.format(s) for s in strings)),
            tuple(fmt_args)
        )