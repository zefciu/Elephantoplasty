from const import NO_ACTION, LIST, RESULT

from eplasty.util import clsname2kname, camel2underscore, diff_unsorted
from eplasty.result import Result
from eplasty.conditions import Equals
from eplasty.relation.many_to_one import ManyToOne

from base import Relation
from eplasty.lazy import LazyQuery

class OneToMany(Relation):
    '''
    Many-to-one relationship on the 'one' side
    '''

    pseudo = True
    compat_types = [list, set]
    columns = []

    def __init__(
        self, foreign_class, backref=None, on_update=NO_ACTION,
        on_delete=NO_ACTION, fmt=LIST, **kwattrs
    ):
        self.prepared = False

        self.foreign_class = foreign_class
        self.backref = backref
        self.fmt = fmt

        super(OneToMany, self).__init__(**kwattrs)



    def bind(self, cls, name):
        self.owner_class = cls
        self.name = name
        if not self.backref:
            self.backref = self.name
            self.kwattrs['backref'] = self.backref
        return self

    def prepare(self): 
        """Called when ready to create a ManyToOne on the other side"""
        self.backref = self.backref or camel2underscore(
            self.owner_class.__name__
        )
        
        if self.backref not in (f.name for f in self.foreign_class.fields):
            self.foreign_field = self.foreign_class.add_field(
                self.backref,
                ManyToOne(foreign_class = self.owner_class)
            )

    def __set__(self, inst, v):
        if isinstance(v, Result):
            raise TypeError, 'Result objects are read-only. Use list instead'
        prev = inst._current.get(self.name, [])
        added, deleted = diff_unsorted(prev, v) #@UnusedVariable
        for obj in added:
            setattr(obj, self.backref, inst)
        inst._current[self.name] = v

    def get_c_vals(self, dict_):
        return {}


    def __get__(self, inst, cls):
        if isinstance(inst._current[self.name], LazyQuery):
            inst._current[self.name] = inst._current[self.name]()
            if self.fmt == LIST:
                inst._current[self.name] = list(inst._current[self.name])
        return inst._current[self.name]

    def hydrate(self, inst, col_vals, dict_, session):
        dict_[self.name] = LazyQuery(
            self.foreign_class, 'find', session,
            Equals(self.foreign_field.column.name, inst.get_pk_value())
        )
