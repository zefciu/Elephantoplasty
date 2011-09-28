import unittest

import eplasty as ep
from util import get_test_conn

class Test(unittest.TestCase):
    """Tests for OneToList relation"""

    def setUp(self):
        class Ingredient(ep.Object):
            name = ep.f.CharacterVarying(20)

        class Meal(ep.Object):
            name = ep.f.CharacterVarying(20)
            ingredients = ep.rel.OneToList(Ingredient)

        self.connection = get_test_conn()
        ep.set_context(self.connection)
        ep.start_session()

        for meal_name, ingredient_set in [
            ('meal1', ['spam', 'bacon']),
            ('meal2', ['spam', 'eggs', 'bacon']),
            ('meal3', ['spam', 'bacon', 'sausage']),
        ]:
            ingredients = [
                Ingredient(name = ing) for ing in ingredient_set
            ]
            ep.add(*ingredients)
            new_meal = Meal(name = meal_name, ingredients = ingredients)
            ep.add(new_meal)

        ep.commit()

        self.Ingredient = Ingredient
        self.Meal = Meal

    def tearDown(self):
        cur = self.connection.cursor()
        try:
            cur.execute('DROP TABLE ingredients CASCADE;')
            cur.execute('DROP TABLE meals CASCADE;')
            self.connection.commit()
        except ProgrammingError as err:
            pass

    def test_get(self):
        """Test if getting a list from fixture preserves the order"""
        ep.start_session()
        # import pdb; pdb.set_trace()
        meal = self.Meal.get(self.Meal.id == 3)
        self.assertEqual(
            [ingredient.name for ingredient in meal.ingredients],
            ['spam', 'bacon', 'sausage'],
        )
