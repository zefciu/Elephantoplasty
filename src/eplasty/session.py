from psycopg2 import ProgrammingError, InterfaceError
from psycopg2.errorcodes import UNDEFINED_TABLE

from eplasty.util import queue_iterator


class Session(object):
    """
The sessions are orm wrappers of connections. They store the objects
and are able to flush them to database
    """

    def __init__(self, connection):
        self.connection = connection
        self.cursors = []
        self.objects = []
        self.nopk_objects = {}
        self.pk_objects = {}

    def __del__(self):
        self.close()

    def _rollback(self):
        """Rollback the connection and unset ``flushed`` flags"""
        self.connection.rollback()
        for o in self.objects:
            o._flushed = False

    def close(self):
        for c in self.cursors:
            try:
                c.close()
            except InterfaceError:
                pass

    def cursor(self, *args, **kwargs):
        new_cur = self.connection.cursor(*args, **kwargs)
        self.cursors.append(new_cur)
        return new_cur

    def add(self, *os):
        for o in os:
            self.objects.append(o)
            pk = o.get_pk_value()
            if pk:
                self.pk_objects.setdefault(type(o).__table_name__, {})
                self.pk_objects[type(o).__table_name__][pk] = o
            else:
                self.nopk_objects.setdefault(type(o).__table_name__, [])
                self.nopk_objects[type(o).__table_name__].append(o)
            o.bind_session(self)

    def flush(self):
        from eplasty.object.const import UNCHANGED, DELETED
        cursor = self.cursor()
        queue = self.objects[:]
        for o in queue_iterator(queue):
            if o._status != UNCHANGED and not o._flushed:
                if o._has_unflushed_dependencies():
                    queue.append(o)
                    continue
                try:
                    o.flush(self, cursor)
                    o._flushed = True
                except ProgrammingError as e:
                    print e.pgcode
                    if e.pgcode == UNDEFINED_TABLE:
                        cursor.connection.commit()
                        type(o).create_table(cursor)
                        self._rollback()
                        self.flush()
                        return
                    else:
                        raise

        self.connection.commit()
        for o in self.objects:
            if o._flushed and o._status != DELETED:
                o._status = UNCHANGED
                o._flushed = False

        for tname, collection in self.nopk_objects.items():
            self.pk_objects.setdefault(tname, {})
            for o in collection:
                self.pk_objects[tname][o.get_pk_value()] = o
            del collection[:]

    def find_cached(self, table_name, pk_value):
        if not isinstance (pk_value, tuple):
            pk_value = pk_value,
        try:
            return self.pk_objects[table_name][pk_value]
        except KeyError:
            return None

    def commit(self):
        self.flush()
        self.connection.commit()

