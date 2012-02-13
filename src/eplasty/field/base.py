from eplasty.object.const import DELETED, UNCHANGED, UPDATED, MODIFIED
from eplasty.object.exc import LifecycleError
from eplasty import conditions as cond

class Field(object):
    """
    Fields are high-level representation of data stored in Objects.
    a field can represent a column, a set of columns or some remote relation.
    Fields are data descriptors"""

    columns = []
    orphaned = False
    indexes = []
    before_delete = None
    after_delete = None

    def __init__(self, *args, **kwargs):
#        self.kwargs = kwargs
        if 'default' in kwargs:
            self._default = kwargs['default']

    def __get__(self, inst, cls):
        if inst is None:
            return self
        if inst._status == DELETED:
            raise LifecycleError('Cannot access deleted object')
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
                inst.touch()
            else:
                raise TypeError('Type {0} is incompatible with field {1}'.format(
                    type(v), type(self)
                ))
        except NotImplementedError:
            raise TypeError(self.RO_MESSAGE)

    def bind_class(self, cls, name):
        self.owner_class = cls
        self.name = name
        return self

    constraints = []

    def prepare(self):
        pass

    def __eq__(self, other):
        return cond.Equals(self.column, other)
    
    def get_dependencies(self, dict_):
        """
        Gets all the objects that should be flushed before the object
        containing this field
        """
        return []

    def bind_session(self, session):
        """Do whatever needed when owner is added to session. Default NOP"""
        pass
