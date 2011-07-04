from const import NO_ACTION
from base import Relation


class ManyToOne(Relation):
    """Many-to-one relationship on the 'many' side"""
    
    def __init__(
        self, foreign_class, null = True, on_update = NO_ACTION,
        on_delete = NO_ACTION, **kwargs
    ):
        self.foreign_class = foreign_class
        self.foreign_pk = self.foreign_class.get_pk()
        if len(self.foreign_pk) != 1:
            raise TypeError, "Referencing composite pk's not implemented"
        self.foreign_pk = self.foreign_pk[0]
        self.pgtype = self.foreign_pk.pgtype
        self.length = self.foreign_pk.length
        self.on_update = on_update
        self.on_delete = on_delete
        self.compat_types = [foreign_class]
        super(ManyToOne, self).__init__(**kwargs)
        self.attrs.append(foreign_class)
        
    def hydrate(self, value, session):
        return self.foreign_class.get(value, session = session)
        
    @property
    def constraint(self):
        return """FOREIGN KEY ({name}) REFERENCES {f_table} ({f_column}) 
        ON UPDATE {on_update} ON DELETE {on_delete}""".format(
            name = self.name,
            f_table = self.foreign_class.__table_name__,
            f_column = self.foreign_pk.name,
            on_update = self.on_update,
            on_delete = self.on_delete,
        )
        
    def get_raw(self, session):
        return self.__get__(self.owner, type(self.owner)).get_pk_value()
    
    @classmethod
    def get_dependencies(self, value):
        return [value]
