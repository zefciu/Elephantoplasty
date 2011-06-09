'''
Created on Jun 8, 2011

@author: szymon
'''
import unittest
from eplasty.table import Table
from eplasty.column import CharacterVarying, Integer
from test.util import get_connection
from eplasty.ctx import start_session, set_context


class TestGetFind(unittest.TestCase):


    def setUp(self):
        self.connection = get_connection()
        self.cursor = self.connection.cursor()
        
        try:
            self.cursor.execute('DROP TABLE testing;')
        except:
            pass
        
        self.connection.commit()
        
        class TestTable(Table):
            name = 'testing'
            columns = [
                CharacterVarying('surname', length = 40),
                Integer('score'),
            ]
            
        TestTable.create_table(self.connection)
            
        fixture = [
            ('Sir Lancelot', 102),
            ('Sir Galahad', 30),
            ('Sir Robin', 30),
        ]
        
        for k in fixture:
            name, score = k
            TestTable(surname = name, score = score).flush(self.cursor)
            
        self.connection.commit()
        
            
        self.TestTable = TestTable


    def tearDown(self):
        self.cursor.execute('DROP TABLE testing;')
        self.connection.commit()
        pass

    def test_get(self):
        set_context(self.connection)
        start_session()
        knight_got = self.TestTable.get(2)
        self.assertEqual(knight_got.surname, 'Sir Galahad')
        
        

if __name__ == "__main__":
    unittest.main()