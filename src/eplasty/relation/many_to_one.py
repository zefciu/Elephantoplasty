from const import NO_ACTION
from base import Relation
from eplasty.lazy import LazyQuery


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
        self.ColType = type(self.foreign_pk)
        self.on_update = on_update
        self.on_delete = on_delete
        self.null = null
        super(ManyToOne, self).__init__(**kwargs)
        
    def _is_compatible(self, value):
        return isinstance(value, self.foreign_class)

    def bind_class(self, cls, name):
        super(ManyToOne, self).bind_class(cls, name)
        constraint = """FOREIGN KEY ({name}) REFERENCES {f_table} ({f_column}) 
        ON UPDATE {on_update} ON DELETE {on_delete}""".format(
            name=self.name, f_table=self.foreign_class.__table_name__,
            f_column=self.foreign_pk.name, on_update=self.on_update,
            on_delete = self.on_delete,
        )
        length = self.foreign_pk.length
        name = self.name + '_id'
        self.column = self.ColType(
            name=name, length=length, null=self.null, constraint=constraint
        )
        self.columns = [self.column]
        return self

    def hydrate(self, ins, col_vals, dict_, session):
        dict_[self.name] = LazyQuery(
            self.foreign_class,
            'get',
            col_vals[self.column.name]
        )
        
    def get_c_vals(self, dict_):
        return {
            self.column.name:
                dict_[self.name] and dict_[self.name].get_pk_value()
        }

    def __get__(self, inst, cls):
        if isinstance(inst._current[self.name], LazyQuery):
            inst._current[self.name] = inst._current[self.name]()
        return inst._current[self.name]

    def get_dependencies(self, dict_):
        yield dict_[self.name]
