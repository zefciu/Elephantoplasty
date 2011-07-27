import itertools as it

from psycopg2 import ProgrammingError

from eplasty.field import Field
# from eplasty.relation import Relation 
from eplasty.util import clsname2tname
from eplasty.ctx import get_cursor
from psycopg2.errorcodes import UNDEFINED_TABLE
from eplasty.field import SimplePK
from .const import UNCHANGED

class ObjectMeta(type):
    """Metaclass for Object types"""
    
    def __init__(cls, classname, bases, dict_):
        fields = [
            f.bind_class(cls, n)
            for n, f in dict_.items() if isinstance(f, Field)
        ]

        if not fields:
            cls._abstract = True
        else:
            cls._abstract = False
            cls._setup_non_abstract(classname, bases, dict_, fields)
        
        super(ObjectMeta, cls).__init__(classname, bases, dict_)
        
    def _setup_non_abstract(cls, classname, bases, dict_, fields): #@NoSelf
        """Setups the non-abstract class creating primary key if needed and
selecting a table name"""

        cls.parent_classes = [b for b in bases if not b._abstract]
        cls.inh_fields = sum([
            p_cls.fields for p_cls in cls.parent_classes
        ], [])
            
        if '__pk__' not in dict_:
            if cls.parent_classes: 
                dict_['__pk__'] = cls.parent_classes[0].__pk__
            else:
                pk = SimplePK('id')
                fields.insert(0, pk)
                dict_['id'] = pk
                dict_['__pk__'] = ('id',)

        cls.__pk__ = dict_['__pk__']
        dict_.pop('__pk__', None)
        cls.columns = sum((f.columns for f in fields), [])
        cls.inh_columns = sum([
            p_cls.columns for p_cls in cls.parent_classes
        ], [])
            
        cls.fields = fields


        if '__table_name__' in dict_:
            cls.__table_name__ = dict_['__table_name__']
        else:
            cls.__table_name__ = clsname2tname(classname)
            
        dict_.pop('__table_name__', None)

        for f in cls.fields:
            f.prepare()

    def create_table(cls, ctx = None): #@NoSelf
        cursor = get_cursor(ctx)
        column_decls = []
        columns = it.chain(*[f.columns for f in cls.fields])
        constraints = sum([f.constraints for f in cls.fields], [])
        for c in columns:
            if c.declaration:
                column_decls.append(c.declaration) 
        constraints.append('PRIMARY KEY ({0})'.format(','.join(cls.__pk__)))
        command = """CREATE TABLE {tname}
        (
        {columns}
        )
        {inh_clause};""".format(
            tname = cls.__table_name__, columns = ',\n'.join(
                [d[0] for d in column_decls] + constraints
            ), inh_clause = (
                'INHERITS ({0})'.format(', '.join((
                    c.__table_name__ for c in cls.parent_classes)
                )) if cls.parent_classes else ''
            )
        )
        args = sum([d[1] for d in column_decls], [])
        retried = False
        while True:
            try:
                # print cursor.mogrify(command, args)
                cursor.execute(command, args)
                break
            except ProgrammingError as e:
                cursor.connection.rollback()
                if e.pgcode == UNDEFINED_TABLE and not retried:
                    for col in cls.columns:
                        if col.references is not None:
                            col.references.create_table()
                            retried = True
                            break
                    else:
                        raise
                else:
                    raise

        cursor.connection.commit()

    def add_field(cls, name, field): #@NoSelf
        field.bind_class(cls, name)
        cls.fields.append(field)
        cls.columns += field.columns
        setattr(cls, name, field)
        return field

    def hydrate(cls, tup, session): #@NoSelf
        """Hydrates the object from given tuple"""
        self = cls.__new__(cls)
        lst = list(tup)
        col_vals = {}
        self._current = {}
        for col in it.chain(self.columns, self.inh_columns):
            col_vals[col.name] = col.hydrate(lst.pop(0), session)

        for f in self.fields:
            f.hydrate(self, col_vals, self._current, session)

        self._initial = self._current.copy()
        self._status = UNCHANGED
        self._flushed = False

        return self