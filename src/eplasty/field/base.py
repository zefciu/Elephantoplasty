class Field(object):
    """
    Fields are high-level representation of data stored in Objects.
    a field can represent a column, a set of columns or some remote relation.
    Fields are descriptors"""

    def __init__(self, *attrs, **kwattrs):
        self.attrs = attrs
        self.kwattrs = kwattrs
        self.owner = None

    def __get__(self, inst, cls):
        if self._value:
            return self._value
        else:
            self._get_value(self, inst, cls)

    def __set__(self, inst, v):
        self._value = v


    def bind_class(self, cls, name):
        self.owner_class = cls
        self.name = name
        self.kwattrs['owner_class'] = cls
        self.kwattrs['name'] = name
        return self

    def bind_object(self, o):
        copy = type(self)(*self.attrs, **self.kwattrs)
        copy.owner = o
        return copy

    constraints = []

    def prepare(self):
        pass
