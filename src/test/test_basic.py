import unittest
from eplasty import column as c
from eplasty.table import Table
from eplasty.ctx import set_context, start_session, commit, add, get_cursor
from util import get_connection


class Test(unittest.TestCase):
    """
Test of eplasty's basic functionalities. Flat tables without inheritance.
    """

    def setUp(self):
        
        class Knight(Table):
            title = c.CharacterVarying(length = 5, null = False)
            name = c.CharacterVarying(length = 20, null = False)
            nickname = c.CharacterVarying(length = 20, null = True)
            score = c.Integer()
            
        self.Knight = Knight
        set_context(get_connection())
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
        c = get_cursor()
        c.execute('DROP TABLE knights;')
        c.connection.commit()


    def test_get(self):
        k = self.Knight.get(2)
        self.assertEqual(k.title, 'King')
        self.assertEqual(k.name, 'Arthur')
        self.assertEqual(k.nickname, None)
        self.assertEqual(k.score, 20)


if __name__ == "__main__":
    unittest.main()