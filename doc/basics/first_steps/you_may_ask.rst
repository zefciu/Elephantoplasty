-----------------------------------------
You may ask...
-----------------------------------------

If you are new to SQL databases and ORM idea, you may skip this part. However,
if you already had some experience with other ORM's you may wonder:

Why is there no explicit connection or session object? Does Elephantoplasty
suport only one connection and session?:
    Elephantoplasty has support for multiple connections and sessions. However
    as simple things should be simple and most apps don't need them it has also
    and idea of **global context**. All these functions we used like
    ``connect()``, ``start_session()``, ``add()``, ``commit()`` are just
    shorthand equivalents of methods we can call on explicit connections and
    sessions.

Why is there no ``syncdb`` or ``create_all()`` necessary?:
    Elephantoplasty uses EAFP (easier to ask forgiveness than permission)
    strategy while dealing with database. It assumes that database is OK (all
    the tables are created) and if it is not (database returns error) it tries
    to fix it. While this may seem like a crazy idea, the fact is that you
    change the database schema much much less often than you manipulate data, so
    this strategy is very cheap while it simplifes things a lot.

How is my data stored?:
    A class corresponds to a table in a database. The table that stores
    instances of ``Knight`` is called ``knights`` by default. Each instance
    corresponds to a row and the columns have the same names as the fields.
    
What about primary key?:
    As we didn't specify a primary key for our knights, Elephantoplasty assumed,
    that you want the simplest (and most popular) primary key -- a sequential
    integer. By convention it is called ``id``. Elephantoplasty allows you to
    override this default, however it's not possible to create a table withou
    primary key (which isn't a feature you will miss).

