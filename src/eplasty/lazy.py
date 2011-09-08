'''
Helper objects for lazy object loading
'''
import eplasty as ep

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

class LazyManyToMany(object):
    """This object will act as an iterator for ManyToMany relation"""
    def __init__(self, relation, owner_id):
        self.relation = relation
        self.owner_id = owner_id
        self.primary_result = self.relation.PrimaryTable.find(
            None,
            ep.conditions.Equals(self.relation.owner_fk, self.owner_id)
        )

    def __iter__(self):
        return self

    def next(self):
        primary = next(self.result)
        return getattr(primary, self.relation.foreign_fk)
