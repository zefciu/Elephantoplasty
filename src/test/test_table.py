import unittest
from eplasty.table.base import Table
from eplasty.column import CharacterVarying
from eplasty.ctx import get_connection, set_context, start_session, add, commit
from util import get_test_conn


class Test(unittest.TestCase):
    """Some table features that don't fit into basic_test"""

    def setUp(self):
        set_context(get_test_conn())
        start_session()


    def tearDown(self):
        c = get_connection()
        c.cursor().execute('DROP TABLE eggs;')
        c.commit()

    def test_custom_name(self):
        """Creating a table with custom table_name"""
        class Spam(Table):
            __table_name__ = 'eggs'
            meal = CharacterVarying(length = 10)
            
        add(Spam(meal = 'bacon'))
        commit()
        c = get_connection()
        cur = c.cursor()
        cur.execute('SELECT id, meal FROM eggs WHERE 1 = 1;')
        self.assertEqual(cur.fetchone(), (1, 'bacon'))
        

if __name__ == "__main__":
    unittest.main()