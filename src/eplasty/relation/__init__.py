'''
Foreign relationship descriptors
'''
from .const import *
from .base import Relation
from .many_to_one import ManyToOne
from .one_to_many import OneToMany
from .many_to_many import ManyToMany
from eplasty.relation.listlike.one_to_list import OneToList
