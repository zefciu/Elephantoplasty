from collections import namedtuple
import functools as ft

from eplasty.field.base import Field
from eplasty import column as col

BlobData = namedtuple('BlobData', ['data', 'mimetype', 'filename'])

class Blob(Field):
    """The field to store binary values with mimetype and filename. It differs
    from FileField in that it isn't accessed by streaming but by taking the 
    whole binary data at once."""

    def __init__(self, mimetype=None):
        self.fixed_mimetype = mimetype
        super(Blob, self).__init__()

    def bind_class(self, cls, name):
        namec = ft.partial(str.format, '{0}_{1}', name)
        self.blob_column = col.ByteA(namec('blob'))
        self.filename_column = col.CharacterVarying(namec('name'), length=128)
        self.columns = [self.blob_column, self.filename_column]
        if not self.fixed_mimetype:
            self.mime_column = col.CharacterVarying(namec('mime'), length=64)
            self.columns.append(self.mime_column)
        super(Blob, self).bind_class(cls, name)
        return self

    def hydrate(self, inst, col_vals, dict_, session):
        if col_vals[self.blob_column.name] is None:
            dict_[self.name] = None
        else:
            if self.fixed_mimetype:
                mimetype = self.fixed_mimetype
            else:
                mimetype = col_vals[self.mime_column.name]
            blob_data = col_vals[self.blob_column.name]
            dict_[self.name] = BlobData(
                blob_data and blob_data.tobytes(),
                mimetype,
                col_vals[self.filename_column.name],
            )

    def get_c_vals(self, dict_):
        obj = dict_.get(self.name)
        if obj is not None:
            result = {
                self.blob_column.name: obj.data,
                self.filename_column.name: obj.filename,
            }
            if not self.fixed_mimetype:
                result[self.mime_column.name] = obj.mimetype
        else:
            result = {
                self.blob_column.name: None,
                self.filename_column.name: None,
            }
            if not self.fixed_mimetype:
                result[self.mime_column.name] = None
        return result

    def _is_compatible(self, value):
        return isinstance(value, BlobData)
