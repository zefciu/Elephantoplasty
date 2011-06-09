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
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute('DROP TABLE testing;')
        except:
            pass
        
        self.connection.commit()
        
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
        
    def testInsert(self):
        self.TestTable.create_table(ctx = self.connection)
        cur = self.connection.cursor()
        row = self.TestTable(name = 'Jane Doe', score = 102) 
        row.flush(cur)
        cur.execute('SELECT * FROM testing WHERE 1=1')
        r = cur.fetchmany()
        
        self.assertEqual(r, [(1, 'Jane Doe', 102)])

if __name__ == "__main__":
    unittest.main()