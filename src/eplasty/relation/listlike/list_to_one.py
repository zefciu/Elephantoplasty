"""The many(list) side of listlike relation"""
from eplasty.relation import Relation
from eplasty.column import BigSerial, BigInt
from eplasty.lazy import LazyQuery
from eplasty.object.const import UNCHANGED, UPDATED, MODIFIED
from eplasty import conditions as cond

class ListToOneRecord(object):
    """Simple structures that store related object and order"""
    __slots__ = 'object', 'order',
    def __init__(self, object_, order):
        self.object = object_
        self.order = order
    # UNCOMMENT WHEN NEEDED
    # def __eq__(self, other):
    #     return self.object == other.object and self.order == other.order

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
        dict_[self.name] = ListToOneRecord(LazyQuery(
            self.foreign_class, 'get', col_vals[self.column.name]
        ), col_vals[self.order_column.name])

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
        if isinstance(inst._current[self.name].object, LazyQuery):
            inst._current[self.name].object = inst._current[self.name].object()
        return inst._current[self.name].object

    def get_dependencies(self, dict_):
        if dict_.get(self.name) is not None:
            yield dict_[self.name].object

    def __set__(self, inst, v):
        raise TypeError('List2One is read-only. Try from the other side')

    def _set(self, inst, object_, order):
        """This is a backdoor through which the ``one'' side can set value of
        this field. Shouldn't be used in any other circumstances"""
        mod = False
        prev = inst._current.get(self.name, None)
        if object_ is not None:
            curr = ListToOneRecord(object_, order)
            inst._current[self.name] = curr
            if curr != prev:
                mod = True
            self.orphaned = False
        else:
            if self.name in inst._current and prev is not None:
                inst._current[self.name] = None
                mod = True
                self.orphaned = True
        if inst._status in [UNCHANGED, UPDATED] and mod:
            inst._status = MODIFIED
        inst.check_orphan_status()

    def __eq__(self, other):
        return cond.Equals(self.column.name, other.get_pk_value())
