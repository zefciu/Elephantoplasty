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
            return inst._current[self.name]
        except KeyError:
            try:
                return self._default
            except AttributeError:
                raise AttributeError('The field {0} is neither set nor '
                    'has default value'.format(
                        self.name
                    ))

    def __set__(self, inst, v):
        try:
            if self._is_compatible(v):
                inst._current[self.name] = v
            else:
                raise TypeError('Type {0} is incompatible with field {1}'.format(
                    type(v), type(self)
                ))
        except NotImplementedError:
            raise TypeError(self.RO_MESSAGE)

    def _is_compatible(self, v):
        raise NotImplementedError

#    def get_c_vals(self, dict_):
#        return {}


    def bind_class(self, cls, name):
        self.owner_class = cls
        self.name = name
        self.kwargs['owner_class'] = cls
        self.kwargs['name'] = name
        return self

    constraints = []

    def prepare(self):
        pass
    
    def get_dependencies(self, dict_):
        """
        Gets all the objects that should be flushed before the object
        containing this field
        """
        return []
