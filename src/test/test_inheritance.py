import unittest
import eplasty as ep
from eplasty import field as f
from eplasty import Object
from .util import get_test_conn


class Test(unittest.TestCase):

    def setUp(self):
        class Character(Object):
            name = f.CharacterVarying(length = 20)
            
        class Knight(Character):
            nickname = f.CharacterVarying(length = 20)
            
        
        self.connection = get_test_conn()
        ep.set_context(self.connection)
        ep.start_session()
        
        ep.add(Character(name = 'Arthur'))
        ep.add(Character(name = 'Patsy'))
        ep.add(Knight(name = 'Robin', nickname = 'The Brave'))
        ep.add(Knight(name = 'Galahad', nickname = 'The Pure'))
        ep.commit()
        
        self.Character = Character
        self.Knight = Knight
        


    def tearDown(self):
        cur = self.connection.cursor()
        self.connection.rollback()
        cur.execute('DROP TABLE knights;')
        cur.execute('DROP TABLE characters;')
        self.connection.commit()


    def test_find_parent(self):
        characters = self.Character.find()
        names = set([c.name for c in characters])
        self.assertEqual(names, set(['Arthur', 'Patsy', 'Robin', 'Galahad']))
        characters.cursor.close()


if __name__ == "__main__":
    unittest.main()