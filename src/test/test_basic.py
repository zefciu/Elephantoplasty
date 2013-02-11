import unittest

from eplasty import field as f
from eplasty import Object
from eplasty.ctx import set_context, start_session, commit, add, get_connection
from .util import get_test_conn
from eplasty.object import NotFound, TooManyFound
from eplasty.object.exc import LifecycleError

class Test(unittest.TestCase):
    """
Test of eplasty's basic functionalities. Flat tables without inheritance.
    """

    def setUp(self):
        
        class Knight(Object):
            title = f.CharacterVarying(
                length = 5, null = False, default = 'Sir'
            )
            name = f.CharacterVarying(length = 20, null = False)
            nickname = f.CharacterVarying(length = 20, null = True)
            score = f.Integer()
            
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
        start_session()
 
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
        """Basic test for find() classmethod with keyword syntax"""
        knights = self.Knight.find(self.Knight.title == 'Sir')
        names = set((k.name for k in knights))
        self.assertEqual(names, set(['Lancelot', 'Galahad', 'Robin']))
        knights.cursor.close()
        knights2 = self.Knight.find()
        objects = knights2.fetch(10)
        self.assertEqual(len(objects), 4)
        knights2.cursor.close()

    def test_find_some_cols(self):
        """Basic test for find() classmethod only some fields"""
        knight = list(self.Knight.find(
            self.Knight.name == 'Galahad', fields=['title', 'nickname']))[0]
        self.assertEqual(knight.title, 'Sir')
        self.assertEqual(knight.nickname, 'The Pure')
        assert 'name' not in knight._current
        # We still can get this value. Additional query will be performed
        self.assertEqual(knight.name, 'Galahad')
        assert 'name' in knight._current

    def test_find_alternative(self):
        """Test finding with == syntax"""
        start_session()
        knights = self.Knight.find(self.Knight.title == 'Sir')
        names = set((k.name for k in knights))
        self.assertEqual(names, set(['Lancelot', 'Galahad', 'Robin']))
        
        
        
    def test_deft(self):
        """Test of default value"""
        k = self.Knight(name = 'Doris', nickname = 'The Hamster', score = 999)
        add(k)
        commit()
        start_session()
        k_got = self.Knight.get(self.Knight.name == 'Doris')
        self.assertEqual(k_got.title, 'Sir')
        
    def test_change(self):
        k = self.Knight.get(2)
        k.name = 'John'
        commit()
        start_session()
        k_got = self.Knight.get(2)
        self.assertEqual(k_got.name, 'John')

    def test_change_id(self):
        """Changing id should be impossible"""
        k = self.Knight.get(2)
        k.name = 'John'
        commit()
        start_session()
        def broken():
            k =  self.Knight.get(2)
            k.id = 1
            
        self.assertRaises(TypeError, broken)

    def test_incompatible(self):
        k = self.Knight.get(2)
        def broken():
            k.name = 1
        self.assertRaises(TypeError, broken)
        
    def test_not_found(self):
        """Test a get() not finding anything"""
        self.assertRaises(
            NotFound, lambda: self.Knight.get(self.Knight.title == 'Mrs')
        )
        
    def test_too_many(self):
        """Test a get() finding too much"""
        self.assertRaises(TooManyFound, lambda: self.Knight.get(title = 'Sir'))
        
    def test_deletion(self):
        """Test a correct deletion behaviour"""
        k = self.Knight.get(2)
        k.delete()
        self.assertRaises(LifecycleError, lambda: k.name)
        commit()
        ks = list(self.Knight.find())
        self.assertEqual(len(ks), 3)

if __name__ == "__main__":
    unittest.main()
