'''
Foreign relationship descriptors
'''
from eplasty.column import Column

NO_ACTION = 'NO ACTION'
CASCADE = 'CASCADE'

class BelongsTo(Column):
    """Many-to-one relationship on the 'many' side"""
    
    def __init__(
        self, foreign_class, null = True, on_update = NO_ACTION,
        on_delete = NO_ACTION, **kwargs
    ):
        self.foreign_class = foreign_class
        self.foreign_pk = self.foreign_class.get_pk()
        self.pgtype = self.foreign_pk.pgtype
        self.length = self.foreign_pk.length
        self.on_update = on_update
        self.on_delete = on_delete
        self.compat_types = [foreign_class]
        super(BelongsTo, self).__init__(name = None, **kwargs)
        
    def hydrate(self, value):
        return self.foreign_class.get(value)
        
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
        
    @classmethod
    def get_raw(cls, value):
        return value.get_pk_value()
    
    @classmethod
    def get_dependencies(self, value):
        return [value]
