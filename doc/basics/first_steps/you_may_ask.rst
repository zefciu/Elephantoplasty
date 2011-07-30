-----------------------------------------
You may ask...
-----------------------------------------

Especially if you already had some experience with other ORM's you may wonder:

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
    this strategy is very cheap while it simplify things a lot.
