"""Contains AdapterField base class and some common subclasses of it."""

import abc
try:
    from lxml import html
except ImportError:
    html = None
from eplasty.field.one_column import OneColumn
from eplasty import column as c

class AdapterField(OneColumn):
    """AdapterField is a single-column field that knows how to transform a
    selected python type to another. It doesn't create a custom type in the
    backend (unlike TODO: CustomField)."""

    @abc.abstractproperty
    def python_types(self):
        pass

    def _is_compatible(self, value):
        return isinstance(value, self.python_types)

    def get_c_vals(self, dict_):
        if self.name in dict_:
            return {self.column.name: self.from_python(dict_[self.name])}
        else:
            return {}

    def hydrate(self, inst, col_vals, dict_, session):
        dict_[self.name] = self.to_python(col_vals[self.column.name])

class Missing:
    """This class raises error when instantiated."""
    def __init__(self):
        raise self.err

if html:
    class Html(AdapterField):
        """Html is represented by an etree on python side and by text on
        postgres side."""

        python_types = html.HtmlElement
        ColumnType = c.Text

        def to_python(self, value):
            result = html.fromstring(value)
            result.render = lambda: html.tostring(result).decode('utf-8')
            return result

        def from_python(self, value):
            return html.tostring(value, encoding='unicode')
else:
    class Html(Missing):
        """Html is missing. You need to install lxml."""
        err = ImportError('You need to install lxml package to use HTMLField')
