class Field(object):
    """
    Fields are high-level representation of data stored in Objects.
    a field can represent a column, a set of columns or some remote relation.
    Fields are data descriptors"""

    columns = []

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        if 'default' in kwargs:
            self._default = kwargs['default']

    def __get__(self, inst, cls):
        try:
            inst._current.get(self.name, self._default)
        except KeyError:
            raise AttributeError, ('The field {0} is neither set nor'
                'has default value'.format(
                    self.name
                ))

    def __set__(self, inst, v):
        inst._current[self.name] = v

    @property
    def value(self):
        if hasattr(self, '_value'):
            return self._value
        elif hasattr(self, '_default'):
            return self._default
        else:
            raise AttributeError,\
                'Field {0} has neither set nor default value'.format(self.name)
        
    def get_c_vals(self, dict_):
        return {}


    def bind_class(self, cls, name):
        self.owner_class = cls
        self.name = name
        self.kwargs['owner_class'] = cls
        self.kwargs['name'] = name
        return self

    constraints = []

    def prepare(self):
        pass
