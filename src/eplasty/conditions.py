"""Condition objects"""
import abc
import itertools as it
from eplasty.util import prepare_col

class Condition(object):
    """Base class for conditions"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def render(self):
        """Render the condition as SQL snippet"""

    def __and__(self, other):
        return And(self, other)
    
class All(Condition):
    """Get all rows"""
    def render(self):
        """Render the condition as SQL snippet"""
        return '1 = 1', tuple()
    
class Equals(Condition):
    """Simple equality condition"""
    def __init__(self, col_name, value):
        if not isinstance(col_name, basestring):
            col_name = prepare_col(col_name)
        self.col_name = col_name
        self.value = value
        super(Equals, self).__init__()
        
    def render(self):
        return '{0} = %s'.format(self.col_name), (self.value,)

class And(Condition):
    """Logical AND of several conditions"""
    def __init__(self, *args):
        self.args = args
        super(And, self).__init__()
        
    def render(self):
        if len(self.args) == 1:
            return self.args[0].render()
        strings = (c.render()[0] for c in self.args)
        fmt_args = it.chain(*(c.render()[1] for c in self.args))
        
        return (
            ' AND '.join(('({0})'.format(s) for s in strings)),
            tuple(fmt_args)
        )
