---------------------------------------------------
Introduction to Elephantoplasty objects
---------------------------------------------------

As the name suggests, object relational mapper is about objects which map to
data in the relational database. Objects are representation of table rows while
classes represent entire tables. In Elephantoplasty objects that store
persistent data inherit from `py:eplasty.Object` class. This class itself is
abstract and cannot be instantiated. To create an object you have to first
create a child class with several `py:eplasty.Field` attributes. These fields
mostly represent columns of the table, however sometimes they have different
meaning.

As an example let us create a class and some instences of it::
    
    >>> import eplasty as ep
    >>> class Bird(ep.Object)
    ...     species = ep.f.CharacterVarying(length=30)
    ...     voltage = ep.f.Integer(default=0)
    ...     sound = ep.f.CharacterVarying(length=30)
    ...
    >>> parrot = Bird(species='Parrot', voltage='2000', sound='voom')
    >>> swallow = Bird()
    >>> swallow.name = 'Swallow'

As you can see, there are two ways of setting the field values. One is by
passing arguments to constructor, the other - to set them as attributes.
    
Unlike SQLAlchemy_ which has two modes - one with explicit table creation and
one called 'declarative', Elephantoplasty features only 'declarative'. The
database schema is created based on the class declaration. Two things that get
deduced:

.. _SQLAlchemy: http://sqlalchemy.org/

* The table name can be specified with ``__table_name__``. It defaults to the
  pluralization of the class name (here it would be "birds").

* The default primary key is called ``id`` and is a column of type serial_. You
  can also provide a different primary key.
