-----------------------
Elephantoplasty
-----------------------

This is my effort to create an ORM which would take full advantage from
PostgresSQL and asyncio.

Philosophy
---------------

#. PostgresSQL is great. However portable ORM's use it like SQLite. To use
   all features of Postgres we need to drop portability to weaker engines.
#. Simple things should be simple, complicated things should be possible.
   The ORM should guess all the obvious things, but allow to override them.
#. The interaction with persistent objects should be as seamless and 
   pythonic as possible
#. No hydration/dehydration logic is needed for such dynamic language
#. Use asyncio exclusively 
