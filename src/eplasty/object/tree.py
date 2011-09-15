"""Tree logic"""
from eplasty.relation import ManyToOne

def tree(
    cls, dependent = False, parent_field='parent', children_field='children'
):
    """This decorator adds tree logic to object class
    * parent_field - The name of the field pointing to parent
    """

    cls.add_field(parent_field, ManyToOne(
        cls, dependent=dependent, backref=children_field
    ))
    return cls
