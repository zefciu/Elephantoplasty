------------------------------------------
Connections and sessions
------------------------------------------

For our ORM to interact with PostgresSQL engine we need a session. A session
wraps around a database connection. It also contains an object cache that
stores all the objects that have been worked with in it. There are basically
two ways objects can become members of the session:

* By being added to a session via ``.add()`` method.
* By being retrieved from the database via ``.get()`` and ``.find()`` methods.

Never can an object be a member of two sessions at once.

To create a session issue::

    >>> my_session = 
