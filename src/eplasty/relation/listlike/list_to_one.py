"""The many(list) side of listlike relation"""
from eplasty.relation import Relation
from eplasty.column import BigSerial, BigInt

class ListToOne(Relation):
    """This field is indended as backref for OneToList relation. It shouldn't
    be created directly and is read-only."""

    def __init__(self, foreign_class, backref=None):
        self.foreign_class = foreign_class
        self.foreign_pk = self.foreign_class.get_pk()
        self.foreign_pk = self.foreign_pk[0]
        self.ColType = type(self.foreign_pk)
        if self.ColType == BigSerial:
            self.ColType = BigInt
        self.backref = backref
        self.order_column = BigInt(self.foreign_class.order_column_name)
        super(ListToOne, self).__init__()

    def bind_class(self, cls, name):
        super(ListToOne, self).bind_class(cls, name)
        length = self.foreign_pk.length
        name = self.name + '_id'
        col_kwargs = dict(
            name=name, length=length, references=self.foreign_class
        )
        self.column = self.ColType(**col_kwargs)
        self.columns = [self.column]
        self.constraint = """
        FOREIGN KEY ({name}) REFERENCES {f_table} ({f_column}) 
        ON UPDATE CASCADE ON DELETE CASCADE""".format(
            name=self.column.name, f_table=self.foreign_class.__table_name__,
            f_column=self.foreign_pk.name
        )
        self.indexes = [('order_index', [name, self.order_column.name])]
        return self

    @property
    def constraints(self):
        return [self.constraint]

    def hydrate(self, ins, col_vals, dict_, session):
        col_val = col_vals[self.column.name]
        dict_[self.name] = LazyQuery(
            self.foreign_class, 'get', col_val
        )

    def __get__(self, inst, cls):
        if inst is None:
            return self
        if isinstance(inst._current[self.name], LazyQuery):
            inst._current[self.name] = inst._current[self.name]()
        return inst._current[self.name]


    def __set__(self, inst, v):
        raise TypeError('List2One is read-only. Try from the other side')
