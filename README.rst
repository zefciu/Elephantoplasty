-----------------------
Elephantoplasty
-----------------------

This is my effort to create an ORM which would take full advantage from
PostgresSQL. It is currently under steady development.

Philosophy
---------------

#. PostgresSQL is great. However portable ORM's use it like SQLite. To use
   all features of Postgres we need to drop portability to weaker engines.
#. Simple things should be simple, complicated things should be possible.
   The ORM should guess all the obvious things, but allow to override them.
#. Where possible use pythonic EAFP strategy. If database seems to be not
   in sync with ORM try to migrate.
#. The interaction with persistent objects should be as seamless and 
   pythonic as possible

DONE
-----------------

#. Simple tables.
#. Inheritance.
#. Simplest one-to-many and many-to-one
#. Many-to-many
#. EAFP table creation
#. Simplest identities
#. Dependent and independent relations
#. Some documentation
#. Tree decorator for simple ``parent_id`` tree
#. List-like relations

TODO
------------------

#. Dict-like relations
#. Advanced primary keys
#. Concurrency control and conflict detection
#. Advanced identities
#. EAFP table migration
#. Joined loading strategy
#. Full documentation
#. MPTT trees
