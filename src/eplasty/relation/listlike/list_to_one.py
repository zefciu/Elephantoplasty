"""The many(list) side of listlike relation"""
from eplasty.relation import Relation
from eplasty.column import BigSerial, BigInt

class ListToOneRecord(object):
    """Simple structures that store related object and order"""
    __slots__ = 'object', 'order',
    def __init__(self, object_, order):
        self.object = object_
        self.order = order

class ListToOne(Relation):
    """This field is indended as backref for OneToList relation. It shouldn't
    be created directly and is read-only."""

    def __init__(self, foreign_class, backref=None, order_column_name='order'):
        self.foreign_class = foreign_class
        self.foreign_pk = self.foreign_class.get_pk()
        self.foreign_pk = self.foreign_pk[0]
        self.ColType = type(self.foreign_pk)
        if self.ColType == BigSerial:
            self.ColType = BigInt
        self.backref = backref
        self.order_column = BigInt(order_column_name)
        self.orphaned = True
        super(ListToOne, self).__init__()

    def bind_class(self, cls, name):
        super(ListToOne, self).bind_class(cls, name)
        length = self.foreign_pk.length
        name = self.name + '_id'
        col_kwargs = dict(
            name=name, length=length, references=self.foreign_class
        )
        self.column = self.ColType(**col_kwargs)
        self.columns = [self.column, self.order_column]
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

    def get_c_vals(self, dict_):
        return {
            self.column.name: (
                dict_.get(self.name) and
                dict_[self.name].object.get_pk_value()
            ),
            self.order_column.name: dict_.get(self.name) and
            dict_[self.name].order
        }

    def __get__(self, inst, cls):
        if inst is None:
            return self
        if isinstance(inst._current[self.name], LazyQuery):
            inst._current[self.name] = inst._current[self.name]()
        return inst._current[self.name]


    def __set__(self, inst, v):
        raise TypeError('List2One is read-only. Try from the other side')

    def _set(self, inst, object_, order):
        """This is a backdoor through which the ``one'' side can set value of
        this field. Shouldn't be used in any other circumstances"""
        if object_ is not None:
            inst._current[self.name] = ListToOneRecord(object_, order)
            self.orphaned = False
        else:
            inst._current[self.name] = None
            self.orphaned = True
        inst.check_orphan_status()

        
