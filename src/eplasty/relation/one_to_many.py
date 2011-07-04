from const import NO_ACTION, LIST, RESULT

from eplasty.util import clsname2kname, camel2underscore, diff_unsorted
from eplasty.result import Result
from eplasty.conditions import Equals
from eplasty.relation.many_to_one import ManyToOne

from base import Relation

class OneToMany(Relation):
    '''
    Many-to-one relationship on the 'one' side
    '''

    pseudo = True
    compat_types = [list, set]

    def __init__(
        self, foreign_class, backref = None, key_name = None, 
        on_update = NO_ACTION, on_delete = NO_ACTION, fmt = LIST, 
        **kwattrs
    ):
        self.prepared = False

        self.foreign_class = foreign_class
        self.backref = backref
        self.key_name = key_name

        super(OneToMany, self).__init__(**kwattrs)
        self.attrs.append(foreign_class)
        self.kwattrs['backref'] = backref
        self.kwattrs['key_name'] = key_name
        self.kwattrs['on_update'] = on_update
        self.kwattrs['on_delete'] = on_delete
        self.kwattrs['fmt'] = fmt



    def bind(self, cls, name):
        self.owner_class = cls
        self.name = name
        return self

    def prepare(self): 
        """Called when ready to create a ManyToOne on the other side"""
        self.key_name = self.key_name or clsname2kname(
            self.owner_class.__name__
        )
        self.backref = self.backref or camel2underscore(
            self.owner_class.__name__
        )
        
        if self.backref not in self.foreign_class.columns:
            new_col = ManyToOne(name = self.backref, foreign_class = self.owner_class)
            self.foreign_class.columns.append(new_col)
            setattr(self.foreign_class, self.backref, new_col)

    def get_raw(self, session):
        pass

    def __set__(self, inst, v):
        if isinstance(v, Result):
            raise TypeError, 'Result objects are read-only. Use list instead'
        prev = self.__get__(inst, type(inst))
        added, deleted = diff_unsorted(prev, v)
        
        for o in added:
            setattr(o, self.backref, inst)
        for o in deleted:
            setattr(o, self.backref, None)
        super(OneToMany, self).__set__(inst, v)

    def __get__(self, inst, cls):
        try:
            return super(OneToMany, self).__get__(inst, cls)
        except KeyError:
            return []

    def hydrate(self, session):
        res = self.foreign_class.find(
            Equals(self.backref, self.owner.get_pk_value)
        )
        if self.fmt == RESULT:
            return res
        if self.fmt == LIST:
            return list(res)

