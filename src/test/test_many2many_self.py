try:
    import unittest2 as unittest
except ImportError:
    import unittest

from test.util import get_test_conn
import eplasty as ep

class Test(unittest.TestCase):
    """Tests for non-synmetrical many2many inside a table"""
    def setUp(self):
        self.connection = get_test_conn()
        ep.set_context(self.connection)
        ep.start_session()
        class Food(ep.Object):
            name = ep.f.CharacterVarying(20)
            ingredients = ep.rel.ManyToMany()

        spam = Food(name='spam')
        eggs = Food(name='eggs')
        bacon = Food(name='bacon')
        sausage = Food(name='sausage')

        meal1 = Food(name='meal1', ingredients=[spam, bacon])
        meal2 = Food(name='meal2', ingredients=[spam, eggs, bacon])
        meal3 = Food(name='meal3', ingredients=[spam, bacon, sausage])
        ep.add(spam, eggs, bacon, sausage, meal1, meal2, meal3)
        self.Food = Food
        ep.commit()

    def tearDown(self):
        self.connection.rollback()
        cur = self.connection.cursor()
        try:
            cur.execute('DROP TABLE foods CASCADE;')
            cur.execute('DROP TABLE foods_foods CASCADE;')
            self.connection.commit()
        except ProgrammingError:
            pass

    def test_get(self):
        ep.start_session()
        meal1 = self.Food.get(5)
        self.assertSetEqual(
            set([ingredient.name for ingredient in meal1.ingredients]),
            set(['spam', 'bacon'])
        )
