try:
    import unittest2 as unittest
except ImportError:
    import unittest

from test.util import get_test_conn

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

        self.connection = get_test_conn()
        ep.set_context(self.connection)

        spam = Ingredient(name='spam')
        eggs = Ingredient(name='eggs')
        bacon = Ingredient(name='bacon')
        sausage = Ingredient(name='sausage')
        ep.start_session()
        ep.add(spam, eggs, bacon, sausage)
        meal1 = Meal(name='meal1', ingredients=[spam, bacon])
        meal2 = Meal(name='meal2', ingredients=[spam, eggs, bacon])
        meal3 = Meal(name='meal3', ingredients=[spam, bacon, sausage])
        ep.add(meal1, meal2, meal3)
        self.Meal = Meal
        self.Ingredient = Ingredient
        ep.commit()

    def tearDown(self):
        self.connection.rollback()
        cur = self.connection.cursor()
        try:
            cur.execute('DROP TABLE ingredients CASCADE;')
            cur.execute('DROP TABLE meals CASCADE;')
            cur.execute('DROP TABLE meals_ingredients CASCADE;')
            self.connection.commit()
        except ProgrammingError:
            pass

    def test_get(self):
        ep.start_session()
        meal = self.Meal.get(1)
        self.assertEqual(meal.ingredients[1].name, 'bacon') 

    # def test_add(self):
    #     ep.start_session()
    #     meal = self.Meal.get(1)
    #     eggs = self.Ingredient.get(2)
    #     meal.ingredients.append(eggs)
    #     ep.commit()
    #     ep.start_session()
    #     meal = self.Meal.get(1)
    #     self.assertSetEqual(
    #         set([i.name for i in meal.ingredients]),
    #         set(['spam', 'eggs', 'bacon'])
    #     )
        
    def test_replace(self):
        """Replacing full list so __set__ is called"""
        ep.start_session()
        meal = self.Meal.get(1)
        eggs = self.Ingredient.get(2)
        bacon = self.Ingredient.get(3)
        meal.ingredients = [eggs, bacon]
        del meal.ingredients[1]
        ep.commit()
        ep.start_session()
        self.assertSetEqual(
            set([i.name for i in meal.ingredients]),
            set(['eggs'])
        )
