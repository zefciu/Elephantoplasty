"""The one side of listlike relation"""

from eplasty.relation import Relation
from eplasty.relation.listlike.list_to_one import ListToOne
from eplasty.util import camel2underscore, RelationList
from eplasty.conditions import Equals
from eplasty.lazy import LazyQuery

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
        
        self.foreign_field = None
        for field in self.foreign_class.fields:
            if field.name == self.backref:
                self.foreign_field = field
                break

        if not self.foreign_field:
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
            ), order_by = self.foreign_field.order_column, session = session
        )

    def __get__(self, inst, cls):
        if isinstance(inst._current[self.name], LazyQuery):
            inst._current[self.name] = inst._current[self.name]()
            inst._current[self.name] = RelationList(
                self, inst, inst._current[self.name]
            )
        return inst._current[self.name]

    def get_c_vals(self, dict_):
        return {}

    def _is_compatible(self, value):
        return isinstance(value, list)
