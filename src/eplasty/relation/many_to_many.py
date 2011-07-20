import eplasty as ep
from .base import Relation
from eplasty.util import clsname2tname, clsname2kname
from eplasty.table.meta import TableMeta
from eplasty.relation.many_to_one import ManyToOne
# from eplasty import relation as r

class ManyToMany(Relation):
    
    def __init__(self, foreign_class = None, backref = None):
        
        self.prepared = False
        
        self.foreign_class = foreign_class
        self.backref = backref
        
        if self.owner_class:
            self._prepare
            
    def bind(self, cls, name):
        self.owner_class = cls
        self.name = name


    def prepare(self): 
        """This method is called when relation is ready to create it's
        PrimaryTable"""
        if not self.foreign_class:
            self.foreign_class = self.owner_class
            
        if not self.backref:
            self.backref = clsname2tname(self.foreign_class.__name__)
        
        self.owner_fk = clsname2kname(self.owner_class)
        self.foreign_fk = clsname2kname(self.foreign_class)
        primary_table_clsname = (
            self.name.capitalize() + self.foreign_class.__name__
        )
        primary_table_name = '{0}_{1}'.format(
            self.name, self.foreign_class.__table_name__
        )
            
        self.PrimaryTable = TableMeta(
            primary_table_clsname, (ep.Table,), {
                '__table_name__': primary_table_name,
                self.owner_fk: ManyToOne(self.owner_class),
                self.foreign_fk: ManyToOne(self.foreign_class),
                '__fk__': (self.owner_fk, self.foreign_fk),
            }
        )
        
    def get_raw(self, session):
        for it in self.__get__(self, type(self)):
            foreign_id = it.get_pk_value()[0]
            self_id = self.get_pk_value()[0]
            
            new_prim = self.PrimaryTable(**{
                self.owner_fk: self_id,
                self.foreign_fk: foreign_id
            })
 
            session.add(new_prim)
    
    def hydrate(self, value, session):
        pass 
