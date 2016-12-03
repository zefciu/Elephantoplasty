class Field():
    def get_columns(self):
        return []


class SingleColumnField(Field):
    """A field represented by a single column"""

    def __init__(self):
        self.column = type(self).ColumnType()

    def get_columns(self):
        yield self.column

    def __get__(self, inst, cls):
        if inst is None:
            return self
        return self.column.get(inst)

    def __set__(self, inst, value):
        self.column.set(inst, value)
