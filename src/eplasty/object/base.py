from collections import OrderedDict
from eplasty.field.base import Field


class ObjectMeta(type):
    """Metaclass for Elephantoplasty objects"""
    def __init__(cls, name, bases, dict_):
        i = 0
        for k, v in dict_.items():
            if isinstance(v, Field):
                for column in v.get_columns():
                    column.index = i
                    i += 1
        cls.tuple_length = i

    @classmethod
    def __prepare__(mcls, name, bases):
        return OrderedDict()


class Object(metaclass=ObjectMeta):
    """Base for Elephantoplasty objects"""

    def __init__(self):
        self.__list__ = [None] * type(self).tuple_length

    @classmethod
    def from_tuple(cls, tuple):
        obj = cls.__new__(cls)
        obj.__list__ = list(tuple)
        return obj
