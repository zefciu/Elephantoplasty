import unittest
from eplasty import column as c
from eplasty.table import Table
from eplasty.ctx import set_context, start_session, commit, add, get_connection
from util import get_test_conn

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
        
    def test_deft(self):
        k = self.Knight(name = 'Doris', nickname = 'The Hamster', score = 999)
        add(k)
        commit()
        k_got = self.Knight.get(name = 'Doris')
        self.assertEqual(k_got.title, 'Sir')
        
    def test_change(self):
        k = self.Knight.get(2)
        k.name = 'John'
        commit()
        k_got = self.Knight.get(2)
        self.assertEqual(k_got.name, 'John')


if __name__ == "__main__":
    unittest.main()