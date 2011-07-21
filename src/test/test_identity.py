import unittest

import eplasty as ep
from eplasty import field as f
from .util import get_test_conn


class Test(unittest.TestCase):


    def setUp(self):
        class Knight(ep.Object):
            title = f.CharacterVarying(
                length = 5, null = False, default = 'Sir'
            )
            name = f.CharacterVarying(length = 20, null = False)
            nickname = f.CharacterVarying(length = 20, null = True)
            score = f.Integer()
            
        self.Knight = Knight
        ep.set_context(get_test_conn())
        ep.start_session()
        
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
            ep.add(k)
            
        ep.commit()


    def tearDown(self):
        c = ep.get_connection()
        c.cursor().execute('DROP TABLE knights;')
        c.commit()


    def test_identical(self):
        """Test if a record is the changed one from cache"""
        knight = self.Knight.get(1)
        knight.title = 'Sire'
        knight2 = self.Knight.get(1)
        self.assertEqual(knight2.title, 'Sire')
        
    def test_not_identical(self):
        """Disabling cache by restarting session"""
        knight = self.Knight.get(1)
        knight.title = 'Sire'
        ep.start_session()
        knight2 = self.Knight.get(1)
        self.assertEqual(knight2.title, 'Sir')
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()