'''
Various utilities.
'''

import re
import types

CAPITAL = re.compile('[A-Z]')

def camel2underscore(v):
    """Transforms CamelCasedName to underscored_name"""
    first = v[0].lower()
    rest = v[1:]
    return first + re.sub(CAPITAL, lambda x: '_' + x.group(0).lower(), rest)

def clsname2tname(clsname):
    """Transforms the class name into default table name"""
    sing = camel2underscore(clsname)
    if sing[-1] == 'y':
        return sing[:-1] + 'ies'
    else:
        return sing + 's'
    
def clsname2kname(clsname):
    """Transforms the class name into foreign key name"""
    underscored = camel2underscore(clsname)
    return '{0}_id'.format(underscored)

def prepare_col(col):
    """Checks if the given column is a tuple and reformats it to fit
    PostgresSQL syntax"""
    if isinstance(col, tuple):
        return '({0})'.format(','.join(col))
    else:
        return col
    
    
    
class queue_iterator(object):
    """This list iterator uses ``pop()`` to iterate over a list, so it empties
    a list and allows to append stuff to the list while iterating"""
    
    def __init__(self, list_):
        self.list_ = list_
        
    def __iter__(self):
        return self
    
    def next(self):
        try:
            return self.list_.pop(0)
        except IndexError:
            raise StopIteration

def diff_unsorted(prev, curr):
    deleted = []
    added = []
    for o in prev:
        if o not in curr:
            deleted.append(o)
            
    for o in curr:
        if o not in prev:
            added.append(o)
    
    return added, deleted

class TraceableList(list):
    """This is a list subclass that calls a given callback when changed"""
    pass

class _TraceableOverride(object):
    """Callable used to overwrite list methods"""

    def __init__(self, method_name):
        self.__name__ = self.method_name = method_name

    def __call__(self, owner, *args, **kwargs):
        prev = owner[:]
        getattr(super(TraceableList, owner), self.method_name)(*args, **kwargs)
        now = owner[:]
        owner.callback(prev, now)

    def __get__(self, inst, type):
        return types.MethodType(self, inst, type)

for method_name in ['pop', 'insert']:
    setattr(TraceableList, method_name, _TraceableOverride(method_name))
