-----------------------------------------------
Introduction to Elephantoplasty
-----------------------------------------------

Elephantoplasty is an Object Relational Manager to work with PostgresSQL_
databases. It is intended to be simple in use, to embrace all features of
PostgresSQL and to make working with relational database as pythonish as
possible.

.. _PostgresSQL: http://www.postgresql.org/

Elephantoplasty differs from other popular ORM systems. It doesn't (and will
never try to) support simple database engines like SQLite or MySQL. Unlike
non-opinionatet SQLAlchemy_ it adheres to "convention over configuration"
principle and tries to do the obvious thing if not explicitly told not to. It
also doesn't try to be a full-blown db toolkit, relying on Psycopg2_ when it
comes to issuing queries. 

.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Psycopg2: http://www.initd.org/psycopg/

