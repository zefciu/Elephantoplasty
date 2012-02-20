"""Session class definition"""
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

    def _rollback(self, clean=False):
        """Rollback the connection and unset ``flushed`` flags"""
        if clean:
            self.connection.rollback_clean()
        else:
            self.connection.rollback()
            self.connection.savepoint = None
        for object_ in self.objects:
            object_._flushed = False

    def close(self):
        """Close the session and all underlying cursors"""
        for cursor in self.cursors:
            try:
                cursor.close()
            except InterfaceError:
                pass

    def cursor(self, *args, **kwargs):
        """Get a new cursor for this session's connection"""
        new_cur = self.connection.cursor(*args, **kwargs)
        self.cursors.append(new_cur)
        return new_cur

    def add(self, *objects):
        """Add objects to session"""
        for object_ in objects:
            self.objects.append(object_)
            primary_key = object_.get_pk_value()
            if primary_key:
                self.pk_objects.setdefault(type(object_).__table_name__, {})
                self.pk_objects[type(object_).__table_name__][primary_key] =\
                        object_
            else:
                self.nopk_objects.setdefault(type(object_).__table_name__, [])
                self.nopk_objects[type(object_).__table_name__].append(object_)
            object_.bind_session(self)

    def flush(self):
        """Flush all pending changes of this session to a database
        (doesn't commit)"""
        from eplasty.object.const import UNCHANGED, DELETED
        cursor = self.cursor()
        queue = self.objects[:]
        for object_ in queue_iterator(queue):
            if object_._status != UNCHANGED and not object_._flushed:
                if object_._has_unflushed_dependencies():
                    queue.append(object_)
                    continue
                try:
                    object_.flush(self, cursor)
                    object_._flushed = True
                except ProgrammingError as err:
                    if err.pgcode == UNDEFINED_TABLE:
                        self._rollback(True)
                        type(object_).create_table(cursor)
                        self.flush()
                        return
                    else:
                        self._rollback(False)
                        raise

        self.connection.commit()
        for object_ in self.objects:
            if object_._flushed and object_._status != DELETED:
                object_._status = UNCHANGED
                object_._flushed = False

        for tname, collection in self.nopk_objects.items():
            self.pk_objects.setdefault(tname, {})
            for object_ in collection:
                self.pk_objects[tname][object_.get_pk_value()] = object_
            del collection[:]

    def find_cached(self, table_name, pk_value):
        """Try to find an object with given identity (table_name and pk)
        in the session cache. If not found returns None.
        """
        if not isinstance (pk_value, tuple):
            pk_value = pk_value,
        try:
            return self.pk_objects[table_name][pk_value]
        except KeyError:
            return None

    def commit(self):
        """Perform flush and commit the transaction"""
        self.flush()
        self.connection.commit()
