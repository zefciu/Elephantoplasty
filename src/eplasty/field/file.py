import functools as ft

from psycopg2.extensions import lobject

from eplasty.field.base import Field
from eplasty import column as col
from eplasty.object.exc import LifecycleError

class TracedLObject(lobject):
    def write(self, *args, **kwargs):
        result = super(TracedLObject, self).write(*args, **kwargs)
        self.connection.save()
        return result

    def export(self, *args, **kwargs):
        result = super(TracedLObject, self).write(*args, **kwargs)
        self.connection.save()
        return result

class _LazyLobject(object):
    """Simple lazy objects that store data for not loaded lobjects. Not to be
    created directly"""
    def __init__(self, oid=None, filename=None, mimetype=None):
        self.oid = oid
        self.filename = filename
        self.mimetype = mimetype

class FileField(Field):
    """Field that stores binary file data together with mimetype. It uses
PostgreSQL large objects, so the files are limited to 2GB."""

    def __init__(self, mimetype=None):
        self.fixed_mimetype = mimetype

    def bind_class(self, cls, name):
        namec = ft.partial(str.format, '{0}_{1}', name)
        self.filename_column = col.CharacterVarying(namec('name'), length=128)
        self.oid_column = col.OID(namec('oid'))
        self.columns = [self.oid_column, self.filename_column]
        if not self.fixed_mimetype:
            self.mime_column = col.CharacterVarying(namec('mime'), length=64)
            self.columns.append(self.mime_column)
        super(FileField, self).bind_class(cls, name)
        return self

    def __set__(self, inst, value):
        raise AttributeError(
            u'Assignment to FileFields is unsupported. Write to the file'
            'instead.'
        )

    def _get_existing(self, inst):
        if self.name in inst._current and inst._current[self.name] is not None:
            if isinstance(inst._current[self.name], _LazyLobject):
                inst._current[self.name] = inst.session.connection.lobject(
                    inst._current[self.name].oid, 'rw', 0, None, TracedLObject
                )
            return inst._current[self.name]

    def __get__(self, inst, cls):
        if not inst.session:
            raise LifecycleError(
                'You cannot write to FileFields that are not added to a'
                ' session'
            )
        fobj = self._get_existing(inst)
        if fobj is None:
            fobj = inst.session.connection.lobject(
                0, 'rw', 0, None, TracedLObject
            )
            inst._current[self.name] = fobj
        fobj.connection=inst.session.connection
        return fobj

    def after_delete(self, inst, session, cursor):
        fobj = self._get_existing(inst)
        if fobj is not None:
            fobj.unlink()


    def _get_mimetype(self, col_vals):
        if self.fixed_mimetype is not None:
            return self.fixed_mimetype
        else:
            return col_vals[self.mime_column.name]

    def hydrate(self, inst, col_vals, dict_, session):
        if col_vals[self.oid_column.name] is None:
            dict_[self.name] == None
        dict_[self.name] = _LazyLobject(
            oid = col_vals[self.oid_column.name],
        )

    def get_c_vals(self, dict_):
        if self.name in dict_ and dict_[self.name] is not None:
            return {
                self.oid_column.name: dict_[self.name].oid,
                self.filename_column.name: 'filename',
                self.mime_column.name: 'application/octet-string',
            }
        else:
            return {}
