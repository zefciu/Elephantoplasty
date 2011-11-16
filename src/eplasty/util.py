'''
Various utilities.
'''

import re
import types

CAPITAL = re.compile('[A-Z]')

def camel2underscore(value):
    """Transforms CamelCasedName to underscored_name"""
    first = value[0].lower()
    rest = value[1:]
    return first + re.sub(CAPITAL, lambda x: '_' + x.group(0).lower(), rest)

def clsname2tname(clsname):
    """Transforms the class name into default table name"""
    sing = camel2underscore(clsname)
    if sing[-1] == 'y':
        return sing[:-1] + 'ies'
    else:
        return sing + 's'
    
# def clsname2kname(clsname):
#     """Transforms the class name into foreign key name"""
#     underscored = camel2underscore(clsname)
#     return '{0}_id'.format(underscored)

def prepare_col(col):
    """Checks if the given column is a tuple and reformats it to fit
    PostgresSQL syntax"""
    if isinstance(col, tuple):
        return '({0})'.format(','.join((c.render_full() for c in col)))
    else:
        return col.name

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
    """Compares two lists. Returns a tuple of added,deleted elements.
    Ignores order modifications"""
    deleted = []
    added = []
    for object_ in prev:
        if object_ not in curr:
            deleted.append(object_)
            
    for object_ in curr:
        if object_ not in prev:
            added.append(object_)
    
    return added, deleted


def index_cmd(table_name, index_declaration):
    """Given and index in form (name, [columns]) returns SQL declaration"""
    index_name, columns = index_declaration
    return """CREATE INDEX {index_name} ON {table_name}
        USING btree ({columns})""".format(
            index_name=index_name, table_name=table_name,
            columns = ', '.join(('"{0}"'.format(c) for c in columns))
        )

class TraceableList(list):
    """This is a list subclass that calls a given callback when changed"""
    pass

class _TraceableOverride(object):
    """Callable used to overwrite list methods"""

    def __init__(self, method_name):
        self.__name__ = self.method_name = method_name

    def __call__(self, owner, *args, **kwargs):
        prev = owner[:]
        result = getattr(
            super(TraceableList, owner), self.method_name
        )(*args, **kwargs)
        now = owner[:]
        owner.callback(prev, now)
        return result

    def __get__(self, inst, type):
        return types.MethodType(self, inst, type)

for method_name in ['pop', 'insert', 'append']:
    setattr(TraceableList, method_name, _TraceableOverride(method_name))

class RelationList(TraceableList):
    """List subclass for managing relationship collections"""
    def __init__(self, owner, inst, it):
        self.inst = inst
        self.owner = owner
        super(RelationList, self).__init__(it)

    def callback(self, was_, is_):
        self.owner._resolve_diff(self.inst, was_, is_)

