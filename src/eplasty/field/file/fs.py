import codecs
from eplasty.field.file.base import BaseFileField

class FSFile(object):
    """File object managing the file stored in filesystem and it's
    corresponding temporary file
    """
    __slots__ = 'field', 'directory', 'filename', 'mimetype'

    def __init__(self, field, directory=None, filename=None, mimetype=None):
        self.field = field
        self.directory = directory
        self.filename = filename
        self.mimetype = mimetype
        self.full_path = os.path.join(
            self.field.root, self.directory, self.filename
        )
        self.tmp_path = self.full_path + '.tmp'


    def open(self, mode='r', encoding=None):
        if not os.path.exists(self.tmp_path):
            os.copy(self.full_path, self.tmp_path)
        open_fn = (
            ft.partial(codecs.open, encoding=encoding) if encoding else open
        )
        return open_fn(self.tmp_path, mode)

    def commit(self):
        os.move(self.tmp_path, self.full_path)

    def rollback(self):
        os.remove(self.tmp_path)



    class FSFileField(BaseFileField):
        """FileField implementation that stores data in filesystem"""

        def __init__(self, name, root, *args, **kwargs):
            super(FSFileField, self).__init__(name, *args, **kwargs)
            self.root = root
            self.dir_column = CharacterVarying(self.name + '_name')
            self.columns.append(self.dir_column)

        def hydrate(self, inst, col_vals, dict_, session):
            dict_[self.name] = FSFile(
                field=self, directory=col_vals[self.dir_column.name],
                filename=col_vals[self.filename],
                mimetype=col_vals[self.mime_column]
            )

        def __get__(self, inst, cls):
            try:
                return super(FSFileField, self).__get__(inst, cls)
            except AttributeError: #Is it always the expected AE?
                inst._current[self.name] = FSFile(field=self)
                return super(FSFileField, self).__get__(inst, cls)

        def commit(self, inst):
            if self.name in inst._current
                inst._current[self.name].commit()
