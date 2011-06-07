import unittest
from eplasty.table import Table
from eplasty.column import CharacterVarying, Integer

from util import get_connection


class Test(unittest.TestCase):

    def setUp(self):
        class TestTable(Table):
            name = 'testing'
            columns = [
                CharacterVarying('name', length = 40),
                Integer('score'),
            ]
            
        self.TestTable = TestTable
        self.connection = get_connection()
        
    def tearDown(self):
        cur = self.connection.cursor()
        cur.execute('DROP TABLE testing;')
        self.connection.commit()
        
    
    def testCreate(self):
        """
        Check if table is correctly created when calling create_table
        explicitly
        """
        
        self.TestTable.create_table(ctx = self.connection)
        cur = self.connection.cursor()
        cur.execute('SELECT * FROM testing WHERE 1=1')
        r = cur.fetchmany()
        
        self.assertEqual(r, [])

if __name__ == "__main__":
    unittest.main()