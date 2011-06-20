'''
Various utilities.
'''

import re

CAPITAL = re.compile('[A-Z]')

def clsname2tname(clsname):
    """Transforms the class name into default table name"""
    first = clsname[0].lower()
    rest = clsname[1:]
    sing = first + re.sub(CAPITAL, lambda x: '_' + x.group(0).lower(), rest)
    if sing[-1] == 'y':
        return sing[:-1] + 'ies'
    else:
        return sing + 's'
    
    
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
