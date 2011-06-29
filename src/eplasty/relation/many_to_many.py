import eplasty as ep
from eplasty.column import Column
from eplasty.util import clsname2tname, clsname2kname
from eplasty.table.meta import TableMeta
from eplasty.relation.many_to_one import ManyToOne
# from eplasty import relation as r

class ManyToMany(Column):
    
    def __init__(self, foreign_class = None, backref = None):
        
        self.prepared = False
        
        self.foreign_class = foreign_class
        self.backref = backref
        
        if self.owner_class:
            self._prepare
            
    def bind(self, cls, name):
        self.owner_class = cls
        self.name = name
        self._prepare()
        
    def _prepare(self): 
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