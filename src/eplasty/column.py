class Column():
    """Base column"""

    def get(self, inst):
        return inst.__list__[self.index]

    def set(self, inst, value):
        inst.__list__[self.index] = value


class VarChar(Column):
    pass


class Integer(Column):
    pass
