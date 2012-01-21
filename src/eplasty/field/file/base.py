import abc

from eplasty.field.base import Field
from eplasty.column import CharacterVarying

class BaseFileField(Field):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, *args, **kwargs):
        self.name=name
        self.mime_column = CharacterVarying(self.name + '_mime')
        self.name_column = CharacterVarying(self.name + '_name')
        self.mimetype = kwargs.get('mimetype', None)
        self.filename = kwargs.get('filename', None)
        self.columns = [self.mime_column, self.name_column]

    @abc.abstractmethod
    def open(self, mode='r', encoding=None):
        pass

    @abc.abstractmethod
    def commit(self):
        pass

    def __set__(self, inst, v):
        raise TypeError(
            u'File attributes cannot be set this way. Write to it or'
            u'modify its attributes instead'
        )
