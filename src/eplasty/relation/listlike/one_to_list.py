"""The one side of listlike relation"""

from eplasty.relation import Relation
from eplasty.relation.listlike.list_to_one import ListToOne
from eplasty.util import camel2underscore, RelationList, diff_unsorted
from eplasty.conditions import Equals
from eplasty.lazy import LazyQuery
from eplasty.object.const import UNCHANGED, UPDATED, MODIFIED

class OneToList(Relation):
    """Listlike relation. It is intended to behave fully as persistent pythonic
    list . """

    def __init__(self, foreign_class, backref=None):
        self.foreign_class = foreign_class
        self.backref = backref
        super(OneToList, self).__init__()

    # def bind_class(self, cls, name):
    #     self.owner_class = cls
    #     self.name = name
    #     return self

    def prepare(self): 
        """Called when ready to create a ManyToOne on the other side"""
        self.backref = self.backref or camel2underscore(
            self.owner_class.__name__
        )
        
        self.foreign_field = self.foreign_class.add_field(
           self.backref,
           ListToOne(
               foreign_class=self.owner_class
           ),
        )

    def hydrate(self, inst, col_vals, dict_, session):
        dict_[self.name] = LazyQuery(
            self.foreign_class, 'find', 
            Equals(
                self.foreign_field.column.name, inst.get_pk_value()
            ), order = [(self.foreign_field.order_column, 'ASC')],
            session = session
        )

    def _resolve_diff(self, inst, prev, curr):
        added, deleted = diff_unsorted(prev, curr) #@UnusedVariable
        for obj in deleted:
            self.foreign_field._set(obj, None, None)
        for i, obj in enumerate(curr, start=1):
            self.foreign_field._set(obj, inst, i)


    def __get__(self, inst, cls):
        if isinstance(inst._current[self.name], LazyQuery):
            inst._current[self.name] = inst._current[self.name]()
            inst._current[self.name] = RelationList(
                self, inst, inst._current[self.name]
            )
        return inst._current[self.name]

    def __set__(self, inst, v):
        if not self._is_compatible(v):
            raise TypeError("{0} is not compatible with OneToList".format(
                type(v)
            ))
        prev = inst._current.get(self.name, [])
        self._resolve_diff(inst, prev, v)
        inst._current[self.name] = v
        if inst._status in [UNCHANGED, UPDATED]:
            inst._status = MODIFIED

    def get_c_vals(self, dict_):
        return {}

    def _is_compatible(self, value):
        return isinstance(value, list)
