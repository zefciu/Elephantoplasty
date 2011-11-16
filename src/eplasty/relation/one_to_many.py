from .const import LIST

from eplasty.util import camel2underscore, diff_unsorted, RelationList
from eplasty.result import Result
from eplasty.conditions import Equals
from eplasty.relation.many_to_one import ManyToOne

from .base import Relation
from eplasty.lazy import LazyQuery

class OneToMany(Relation):
    '''
    Many-to-one relationship on the 'one' side
    '''

    compat_types = [list, set]
    columns = []


    def __init__(
        self, foreign_class, backref=None, dependent=False, fmt=LIST,
        **kwattrs
    ):
        self.prepared = False

        self.foreign_class = foreign_class
        self.backref = backref
        self.fmt = fmt
        self.dependent = dependent
        


        super(OneToMany, self).__init__(**kwattrs)

    def bind_class(self, cls, name):
        self.owner_class = cls
        self.name = name
        return self

    def prepare(self): 
        """Called when ready to create a ManyToOne on the other side"""
        self.backref = self.backref or camel2underscore(
            self.owner_class.__name__
        )
        
        self.foreign_field = None
        for field in self.foreign_class.fields:
            if field.name == self.backref:
                self.foreign_field = field
                break

        if not self.foreign_field:
            self.foreign_field = self.foreign_class.add_field(
                self.backref,
                ManyToOne(
                    foreign_class=self.owner_class, dependent=self.dependent
                ),
            )
            

    def __set__(self, inst, v):
        prev = inst._current.get(self.name, [])
        self._resolve_diff(inst, prev, v)
        inst._current[self.name] = v
        
    def _resolve_diff(self, inst, prev, curr):
        added, deleted = diff_unsorted(prev, curr) #@UnusedVariable
        for obj in added:
            setattr(obj, self.backref, inst)
        for obj in deleted:
            setattr(obj, self.backref, None)

    def get_c_vals(self, dict_):
        return {}


    def __get__(self, inst, cls):
        if isinstance(inst._current[self.name], LazyQuery):
            inst._current[self.name] = inst._current[self.name]()
            if self.fmt == LIST:
                inst._current[self.name] = RelationList(
                    self, inst, inst._current[self.name]
                )
        return inst._current[self.name]

    def hydrate(self, inst, col_vals, dict_, session):
        dict_[self.name] = LazyQuery(
            self.foreign_class, 'find', 
            Equals(
                self.foreign_field.column.name, inst.get_pk_value()
            ), session = session
        )
