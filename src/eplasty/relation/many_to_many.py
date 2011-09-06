import eplasty as ep
from .const import LIST
from .base import Relation
from eplasty.util import clsname2tname, clsname2kname
from eplasty.object.meta import ObjectMeta
from eplasty.relation.many_to_one import ManyToOne

class ManyToMany(Relation):

    compat_types = [list, set]
    columns = []
    
    def __init__(
        self, foreign_class = None, backref = None, fmt=LIST, **kwattrs
    ):
        
        self.prepared = False
        
        self.foreign_class = foreign_class
        self.backref = backref
        self.fmt = fmt
            
    def bind(self, cls, name):
        self.owner_class = cls
        self.name = name
        if not self.backref:
            self.backref = self.name
            self.kwattrs['backref'] = self.backref

    def prepare(self): 
        """This method is called when relation is ready to create it's
        PrimaryTable"""
        if not self.foreign_class:
            self.foreign_class = self.owner_class
        
        self.owner_fk = clsname2kname(self.owner_class)
        self.foreign_fk = clsname2kname(self.foreign_class)
        primary_table_clsname = (
            self.name.capitalize() + self.foreign_class.__name__
        )
        primary_table_name = '{0}_{1}'.format(
            self.name, self.foreign_class.__table_name__
        )
            
        self.PrimaryTable = ObjectMeta(
            primary_table_clsname, (ep.Object,), {
                '__table_name__': primary_table_name,
                self.owner_fk: ManyToOne(self.owner_class),
                self.foreign_fk: ManyToOne(self.foreign_class),
                '__pk__': (self.owner_fk, self.foreign_fk),
            }
        )
        
    def hydrate(self, value, session):
        pass 
