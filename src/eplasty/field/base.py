class Field(object):
    """
    Fields are high-level representation of data stored in Objects.
    a field can represent a column, a set of columns or some remote relation.
    Fields are data descriptors"""

    columns = []

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.owner = None
        if 'default' in kwargs:
            self._default = kwargs['default']

    def __get__(self, inst, cls):
        if self._value:
            return self._value
        else:
            self._get_value(self, inst, cls)

    def __set__(self, inst, v):
        self._value = v
        
    @property
    def value(self):
        if hasattr(self, '_value'):
            return self._value
        elif hasattr(self, '_default'):
            return self._default
        else:
            raise AttributeError,\
                'Field {0} has neither set nor default value'.format(self.name)
        


    def bind_class(self, cls, name):
        self.owner_class = cls
        self.name = name
        self.kwargs['owner_class'] = cls
        self.kwargs['name'] = name
        return self

    def bind_object(self, o):
        copy = type(self)(**self.kwargs)
        copy.owner = o
        return copy

    constraints = []

    def prepare(self):
        pass
