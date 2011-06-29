import unittest
from eplasty import column as c
from eplasty.table import Table
from eplasty.ctx import set_context, start_session, commit, add, get_connection
from util import get_test_conn
from eplasty.table.exc import NotFound, TooManyFound

class Test(unittest.TestCase):
    """
Test of eplasty's basic functionalities. Flat tables without inheritance.
    """

    def setUp(self):
        
        class Knight(Table):
            title = c.CharacterVarying(
                length = 5, null = False, default = 'Sir'
            )
            name = c.CharacterVarying(length = 20, null = False)
            nickname = c.CharacterVarying(length = 20, null = True)
            score = c.Integer()
            
        self.Knight = Knight
        set_context(get_test_conn())
        start_session()
        # Knight.create_table()
        
        for ktup in [
            ('Sir', 'Galahad', 'The Pure', 10),
            ('King', 'Arthur', None, 20),
            ('Sir', 'Robin', 'The Brave', 30),
            ('Sir', 'Lancelot', None, 40),
        ]:
            title, name, nickname, score = ktup
            k = Knight(
                title = title,
                name = name,
                nickname = nickname,
                score = score
            )
            add(k)
            
        commit()
 
    def tearDown(self):
        c = get_connection()
        c.cursor().execute('DROP TABLE knights;')
        c.commit()


    def test_get(self):
        k = self.Knight.get(2)
        self.assertEqual(k.title, 'King')
        self.assertEqual(k.name, 'Arthur')
        self.assertEqual(k.nickname, None)
        self.assertEqual(k.score, 20)
        
    def test_find(self):
        knights = self.Knight.find(title = 'Sir')
        names = set((k.name for k in knights))
        self.assertEqual(names, set(['Lancelot', 'Galahad', 'Robin']))
        knights.cursor.close()
        knights2 = self.Knight.find()
        objects = knights2.fetch(10)
        self.assertEqual(len(objects), 4)
        knights2.cursor.close()
        
        
        
        
    def test_deft(self):
        k = self.Knight(name = 'Doris', nickname = 'The Hamster', score = 999)
        add(k)
        commit()
        start_session()
        k_got = self.Knight.get(name = 'Doris')
        self.assertEqual(k_got.title, 'Sir')
        
    def test_change(self):
        k = self.Knight.get(2)
        k.name = 'John'
        commit()
        k_got = self.Knight.get(2)
        self.assertEqual(k_got.name, 'John')
        
    def test_incompatible(self):
        k = self.Knight.get(2)
        def broken():
            k.name = 1
        self.assertRaises(TypeError, broken)
        
    def test_not_found(self):
        """Test a get() not finding anything"""
        self.assertRaises(NotFound, lambda: self.Knight.get(title = 'Mrs'))
        
    def test_too_many(self):
        """Test a get() finding too much"""
        self.assertRaises(TooManyFound, lambda: self.Knight.get(title = 'Sir'))

if __name__ == "__main__":
    unittest.main()