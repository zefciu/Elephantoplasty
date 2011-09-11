import eplasty as ep
from .const import LIST
from .base import Relation
from eplasty.util import (
    clsname2tname, camel2underscore, diff_unsorted, RelationList
)
from eplasty.object.meta import ObjectMeta
from eplasty.result import Result
from eplasty.object.base import NotFound
from eplasty.relation.many_to_one import ManyToOne
from eplasty.lazy import LazyManyToMany

class ManyToMany(Relation):

    compat_types = [list, set]
    columns = []
    
    def __init__(
        self, foreign_class = None, backref = None, fmt=LIST, **kwargs
    ):
        
        self.prepared = False
        
        self.foreign_class = foreign_class
        self.backref = backref
        self.fmt = fmt
        super(ManyToMany, self).__init__(**kwargs)
            
    def bind(self, cls, name):
        self.owner_class = cls
        self.name = name
        if not self.backref:
            self.backref = self.name

    def prepare(self): 
        """This method is called when relation is ready to create it's
        PrimaryTable"""
        if not self.foreign_class:
            self.foreign_class = self.owner_class
        
        self.owner_fk = camel2underscore(self.owner_class.__name__)
        self.foreign_fk = camel2underscore(self.foreign_class.__name__)
        if self.owner_fk == self.foreign_fk:
            self.owner_fk = self.owner_fk + '1'
            self.foreign_fk = self.foreign_fk + '2'
        primary_table_clsname = (
            self.owner_class.__name__ + self.foreign_class.__name__
        )
        primary_table_name = '{0}_{1}'.format(
            self.owner_class.__table_name__, self.foreign_class.__table_name__
        )
            
        self.PrimaryTable = ObjectMeta(
            primary_table_clsname, (ep.Object,), {
                '__table_name__': primary_table_name,
                self.owner_fk: ManyToOne(self.owner_class),
                self.foreign_fk: ManyToOne(self.foreign_class),
                '__pk__': (self.owner_fk + '_id', self.foreign_fk + '_id'),
            }
        )
        
    def hydrate(self, inst, col_vals, dict_, session):
        dict_[self.name] = LazyManyToMany(self, inst.session, inst.get_pk_value())

    def __set__(self, inst, v):
        if isinstance(v, Result):
            raise TypeError('Result objects are read-only. Use list instead')
        prev = inst._current.get(self.name, [])
        self._resolve_diff(inst, prev, v)
        inst._current[self.name] = v
        
    def _resolve_diff(self, inst, prev, curr):
        added, deleted = diff_unsorted(prev, curr) #@UnusedVariable
        self.temporary = []
        for obj in added:
            new_primary = self.PrimaryTable()
            setattr(new_primary, self.owner_fk, inst)
            setattr(new_primary, self.foreign_fk, obj)
            inst.add(new_primary)
        if inst.session is not None:
            for obj in deleted:
                try:
                    to_delete = inst.session.get(
                        Equals(self.owner_fk, inst.get_pk_value() &
                        Equals(self.foreign_fk, obj.get_pk_value()))
                    )
                except NotFound:
                    continue
                to_delete.delete()


    def __get__(self, inst, cls):
        if isinstance(inst._current[self.name], LazyManyToMany):
            inst._current[self.name] = list(inst._current[self.name])
        inst._current[self.name] = RelationList(
            self, inst, inst._current[self.name]
        )
        return inst._current[self.name]

    def __set__(self, inst, v):
        if isinstance(v, Result):
            raise TypeError('Result objects are read-only. Use list instead')
        prev = inst._current.get(self.name, [])
        self._resolve_diff(inst, prev, v)
        inst._current[self.name] = v

    def _is_compatible(self, value):
        return isinstance(value, (list, set))

    def get_c_vals(self, dict_):
        return {}

    def bind_session(self, session):
        if self.temporary:
            session.add(*self.temporary)
        self.tempoarary = []
