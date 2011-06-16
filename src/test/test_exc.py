'''
Testing the exception raising of various objects and methods
'''
import unittest

from psycopg2 import ProgrammingError

from eplasty.table import Table
from eplasty.conditions import Condition
from eplasty.column import CharacterVarying
from eplasty.ctx import set_context, add, commit, start_session
from test.util import get_test_conn


class Test(unittest.TestCase):
    """Some simple exceptions"""


    def test_virtual_table(self):
        """Trying to get an instance of a table with no columns"""
        class Abs(Table):
            pass
        self.assertRaises(NotImplementedError, lambda: Abs())
        
    def test_base_condition(self):
        """Trying to render base condition"""
        self.assertRaises(NotImplementedError, lambda: Condition().render())
        
    def test_invalid_column(self):
        """Trying to initialize a row with nonexistent column name"""
        class Spam(Table):
            eggs = CharacterVarying()
        
        self.assertRaises(TypeError, lambda: Spam(bacon = 'sausage'))
        
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
        class Spam(Table):
            bacon = CharacterVarying(length = 10)
        
        add(Spam(bacon = 'sausage'))
        self.assertRaises(ProgrammingError, commit)
        
        
        
            
            
        
        

if __name__ == "__main__":
    unittest.main()