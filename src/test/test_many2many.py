import unittest

from psycopg2 import ProgrammingError

import eplasty as ep

class Test(unittest.TestCase):
    """Basic tests for non-synmetrical many-to-many"""

    def setUp(self):
        class Ingredient(ep.Object):
            name = ep.f.CharacterVarying(20)

        class Meal(ep.Object):
            name = ep.f.CharacterVarying(20)
            ingredients = ep.rel.ManyToMany(Ingredient)

        spam = Ingredient(name='spam')
        eggs = Ingredient(name='eggs')
        bacon = Ingredient(name='bacon')
        sausage = Ingredient(name='sausage')
        ep.start_session()
        ep.add(spam, eggs, bacon, sausage)
        meal1 = Meal(name='meal1', ingredents=[spam, bacon]),
        meal2 = Meal(name='meal2', ingredents=[spam, eggs, bacon]),
        meal3 = Meal(name='meal3', ingredents=[spam, bacon, sausage]),
        ep.add(meal1, meal2, meal3)

    def tearDown(self):
        cur = self.connection.cursor()
        try:
            cur.execute('DROP TABLE ingredients;')
            cur.execute('DROP TABLE meals;')
            self.connection.commit()
        except ProgrammingError:
            pass

    def test_get(self):
        start_session()
        meal = Meal.get(1)
        self.assertEqual(meal.ingredients[1].name, 'bacon') 
