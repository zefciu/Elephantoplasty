import os
import functools as ft
import mimetypes as mt

from psycopg2.extensions import lobject

from eplasty.field.base import Field
from eplasty import column as col
from eplasty.object.exc import LifecycleError

class TracedLObject(lobject):
    
    def __init__(self, *args, **kwargs):
        super(TracedLObject, self).__init__(*args, **kwargs)
        self._mimetype = None
        self.filename = None

    def write(self, *args, **kwargs):
        result = super(TracedLObject, self).write(*args, **kwargs)
        self.connection.save()
        return result

    def import_(self, filename):
        self.filename = os.path.basename(filename)
        with open(filename, 'r') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                self.write(chunk)

    def unlink(self):
        self.inst._current[self.name] = None
        self.inst.touch()
        super(TracedLObject, self).unlink()

    def get_size(self):
        pos = self.tell()
        result = self.seek(0, 2)
        self.seek(pos, 0)
        return result

    def serve(self):
        """Returns a WSGI app that serves this file"""
        def app(environ, start_response):
            start_response('200 OK', [
                ('Content-Type', self.mimetype),
                ('Content-Size', str(self.get_size())),
                ('Content-Disposition', 'attachment; filename="{0}"'.format(
                    self.filename
                ))
            ])
            while True:
                chunk = self.read(4096)
                if not chunk:
                    return
                yield chunk
        return app

    @property
    def mimetype(self):
        if self._mimetype is not None:
            return self._mimetype
        elif self.filename is not None:
            type_, enc = mt.guess_type(self.filename)
            if type_ is not None:
                self._mimetype = type_
                return type_
        return 'application/octet-stream'

    @mimetype.setter
    def mimetype(self, value):
        if self.fixed_mimetype:
            raise AttributeError(
                "This field's mimetype is fixed to {0}".format(self._mimetype)
            )
        self._mimetype = value
            

class _LazyLObject(object):
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
            if isinstance(inst._current[self.name], _LazyLObject):
                lazy = inst._current[self.name]
                real = inst.session.connection.lobject(
                    lazy.oid, 'rw', 0, None, TracedLObject
                )
                real.filename = lazy.filename
                real._mimetype = lazy.mimetype
                real.fixed_mimetype = lazy.fixed_mimetype
                inst._current[self.name] = real
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
        if self.fixed_mimetype:
            fobj.fixed_mimetype = True
            fobj._mimetype = self.fixed_mimetype
        else:
            fobj.fixed_mimetype = False
        fobj.inst = inst
        fobj.name = self.name
        return fobj

    def after_delete(self, inst, session, cursor):
        fobj = self._get_existing(inst)
        if fobj is not None:
            fobj.unlink()


    def hydrate(self, inst, col_vals, dict_, session):
        if col_vals[self.oid_column.name] is None:
            dict_[self.name] = None
        else:
            dict_[self.name] = _LazyLObject(
                oid = col_vals[self.oid_column.name],
                filename = col_vals[self.filename_column.name],
            )
            if not self.fixed_mimetype:
                dict_[self.name].mimetype =\
                    col_vals[self.mime_column.name]
                dict_[self.name].fixed_mimetype = False
            else:
                dict_[self.name].mimetype = self.fixed_mimetype
                dict_[self.name].fixed_mimetype = True


    def get_c_vals(self, dict_):
        if self.name in dict_ and dict_[self.name] is not None:
            fobj = dict_[self.name]
            result = {
                self.oid_column.name: fobj.oid,
                self.filename_column.name: fobj.filename,
            }
            if not self.fixed_mimetype:
                result[self.mime_column.name] = fobj.mimetype
            return result
        else:
            return {
                self.oid_column.name: None,
                self.filename_column.name: None,
            }
