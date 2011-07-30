----------------------------------------------
What we just did
----------------------------------------------

1. The main package in Elephantoplasty is called ``eplasty``. In this
   documentation we assume that we always import it abbreviating even more as
   ``ep``.

3. The function ``connect`` has exactly the same semantics as a method with
   the same name in psycopg :py:func:`psycopg2.connect` and
   is self-explanatory.
   
.. _`method of the same name`: 

7. Everything we do in Elephantoplasty is a part of a session. Here we simply
   start a new, global, empty session.

9. Persistent objects inherit from :py:class:`eplasty.Object`. Namespace
   :py:mod:`eplasty.f` contains fields which represent persistent data stored
   in these objects.

20. We can provide values for new objects either initializing them with
    keywords or by setting their attributes later (as with ``lancelot`` object).

24. For newly created objects to become persistent we must explicitly add them
    to a session.

25. The ``commit()`` function flushes all the changes we've done in this session
    and commits them in a transaction.

27. This isn't necessary, but useful in tests to ensure, that Elephantoplasty
    doesn't use cache but reads from real database.

28. The classmethod ``.find()`` without any arguments finds everything.

31. We clean up the database so we can run this snippet again.

