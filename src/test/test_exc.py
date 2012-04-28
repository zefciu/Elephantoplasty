'''
Testing the exception raising of various objects and methods
'''
import unittest

from psycopg2 import ProgrammingError
from psycopg2.errorcodes import UNDEFINED_OBJECT, UNDEFINED_COLUMN

from eplasty import Object
from eplasty.conditions import Condition
from eplasty.column import Column
from eplasty.field import Simple, CharacterVarying
from eplasty.relation import ManyToOne
from eplasty.ctx import set_context, add, commit, start_session, ctx
from test.util import get_test_conn

class BrokenCol(Column):
    """PostgreSQL integer type"""
    pgtype = 'fondlemybuttocks'
    compat_types = [int]

class BrokenField(Simple):
    ColumnType = BrokenCol

class Test(unittest.TestCase):
    """Some simple exceptions"""


    def test_virtual_table(self):
        """Trying to get an instance of a table with no columns"""
        class Abs(Object):
            pass
        self.assertRaises(NotImplementedError, lambda: Abs())
        
    def test_base_condition(self):
        """Trying to render base condition"""
        self.assertRaises(TypeError, lambda: Condition().render())
        
    def test_invalid_column(self):
        """Trying to initialize a row with nonexistent column name"""
        class Spam(Object):
            eggs = CharacterVarying()
        
        self.assertRaises(TypeError, lambda: Spam(bacon = 'sausage'))
        
    def test_empty_field(self):
        """Trying to get a value of unset field"""
        class Spam(Object):
            eggs = CharacterVarying()
        spam = Spam()
        self.assertRaises(AttributeError, lambda: spam.eggs)
        
    def tearDown(self):
        try:
            conn = get_test_conn()
            conn.cursor().execute('DROP TABLE spams;')
            conn.commit()
            
        except ProgrammingError:
            pass
        
    def test_table_mismatch(self):
        """Testing unhandled errors when flushing"""
        conn = get_test_conn()
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE spams (
                id integer,
                eggs character varying(10),
                PRIMARY KEY (id)
            );""")
        conn.commit()
        set_context(conn)
        start_session()
        class Spam(Object):
            bacon = CharacterVarying(length = 10)
        
        add(Spam(bacon = 'sausage'))
        self.assertRaises(ProgrammingError, commit)

    def test_unhandled_exception(self):
        """Testing the exception from engine that can't be handled"""
        conn = get_test_conn()
        set_context(conn)
        class Spam(Object):
            eggs = BrokenField()
        try:
            Spam.create_table()
        except ProgrammingError as err:
            conn.rollback()
            self.assertEqual(err.pgcode, UNDEFINED_OBJECT)

    def test_unhandled_exception_getting(self):
        """Testing the exception from engine that can't be handled
        (while get()ting)"""
        conn = get_test_conn()
        set_context(conn)
        start_session()
        class Spam(Object):
            eggs = CharacterVarying(20)
        add(Spam(eggs='abc'))
        commit()
        start_session()
        class Spam(Object):
            bacon = CharacterVarying(20)
        try:
            spam = Spam.get(1)
        except ProgrammingError as err:
            self.assertEqual(err.pgcode, UNDEFINED_COLUMN)

    def test_reference_complex_pk(self):
        """Trying to reference complex pk should cause TypeError"""
        def broken():
            class Spam(Object):
                name = CharacterVarying(20)
                surname = CharacterVarying(20)
                __pk__ = ('name', 'surname')

            class Eggs(Object):
                spam = ManyToOne(Spam)

        self.assertRaises(TypeError, broken)



        

if __name__ == "__main__":
    unittest.main()
