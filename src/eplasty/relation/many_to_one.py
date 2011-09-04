from .const import CASCADE, SET_NULL
from .base import Relation
from eplasty.lazy import LazyQuery
from eplasty.column import BigSerial, BigInt


class ManyToOne(Relation):
    """Many-to-one relationship on the 'many' side"""
    
    def __init__(
        self, foreign_class, dependent=False, **kwargs
    ):
        self.foreign_class = foreign_class
        self.foreign_pk = self.foreign_class.get_pk()
        if len(self.foreign_pk) != 1:
            raise TypeError("Referencing composite pk's not implemented")
        self.foreign_pk = self.foreign_pk[0]
        self.ColType = type(self.foreign_pk)
        if self.ColType == BigSerial:
            self.ColType = BigInt
        self.dependent = dependent
        self.orphaned = dependent
        on_update = on_delete = CASCADE if dependent else SET_NULL
        self.on_update = on_update
        self.on_delete = on_delete
        self.null = not dependent
        super(ManyToOne, self).__init__(**kwargs)
        
    def _is_compatible(self, value):
        return isinstance(value, (self.foreign_class, type(None)))

    def orphan(self, inst):
        inst._current[self.name] = NULL
        self.orphaned = True
        inst.set_orphan_status
    
    @property
    def constraints(self):
        return [self.constraint]

    def bind_class(self, cls, name):
        super(ManyToOne, self).bind_class(cls, name)
        length = self.foreign_pk.length
        name = self.name + '_id'
        col_kwargs = dict(name=name, length=length, null=self.null,
            references=self.foreign_class
        )
        if self.null:
            col_kwargs['default'] = None
        self.column = self.ColType(**col_kwargs)
        self.columns = [self.column]
        self.constraint = """
        FOREIGN KEY ({name}) REFERENCES {f_table} ({f_column}) 
        ON UPDATE {on_update} ON DELETE {on_delete}""".format(
            name=self.column.name, f_table=self.foreign_class.__table_name__,
            f_column=self.foreign_pk.name, on_update=self.on_update,
            on_delete = self.on_delete,
        )
        return self

    def hydrate(self, ins, col_vals, dict_, session):
        col_val = col_vals[self.column.name]
        if col_val is not None:
            dict_[self.name] = LazyQuery(
                self.foreign_class, 'get', col_val
            )
        else:
            dict_[self.name] = None
        
    def get_c_vals(self, dict_):
        return {
            self.column.name:
                dict_[self.name] and dict_[self.name].get_pk_value()
        }

    def __get__(self, inst, cls):
        if isinstance(inst._current[self.name], LazyQuery):
            inst._current[self.name] = inst._current[self.name]()
        return inst._current[self.name]

    def __set__(self, inst, v):
        super(ManyToOne, self).__set__(inst, v)
        self.orphaned = False
        inst.check_orphan_status

    def get_dependencies(self, dict_):
        if dict_[self.name] is not None:
            yield dict_[self.name]
            
