try:
    import unittest2 as unittest
except ImportError:
    import unittest

import eplasty as ep
from .util import get_test_conn

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
        self.assertListEqual(
            [ingredient.name for ingredient in meal.ingredients],
            ['spam', 'bacon', 'sausage'],
        )

    def test_backref(self):
        """Test if items are getting correct backref"""
        ep.start_session()
        meal = self.Meal.get(self.Meal.id == 3)
        self.assertEqual(
            meal.ingredients[0].meal,
            meal,
        )

    def test_swap(self):
        """Test if swappin elements from a list from fixture works"""
        ep.start_session()
        meal = self.Meal.get(self.Meal.id == 3)
        ing = meal.ingredients.pop(0)
        meal.ingredients.append(ing)
        ep.commit()
        ep.start_session
        meal = self.Meal.get(self.Meal.id == 3)
        self.assertListEqual(
            [ingredient.name for ingredient in meal.ingredients],
            ['bacon', 'sausage', 'spam'],
        )

    def test_swap_as_new(self):
        """Test swapping, but this time we set a completely new list"""
        ep.start_session()
        meal = self.Meal.get(self.Meal.id == 3)
        new_ings = meal.ingredients[:]
        ing = new_ings.pop(0)
        new_ings.append(ing)
        meal.ingredients = new_ings
        ep.commit()
        ep.start_session
        meal = self.Meal.get(self.Meal.id == 3)
        self.assertListEqual(
            [ingredient.name for ingredient in meal.ingredients],
            ['bacon', 'sausage', 'spam'],
        )

    def test_back_search(self):
        """Test using the backref as a base for condition"""
        ep.start_session()
        meal = self.Meal.get(self.Meal.id == 3)
        ingredients = self.Ingredient.find(self.Ingredient.meal == meal)
        self.assertSetEqual(
            set((ingredient.id for ingredient in meal.ingredients)),
            set((ingredient.id for ingredient in ingredients)),
        )

    def test_wrong_side(self):
        """Trying to write to the backref"""
        ep.start_session()
        meal1 = self.Meal.get(self.Meal.id == 1)
        meal2 = self.Meal.get(self.Meal.id == 2)
        def wrong():
            meal1.ingredients[0].meal = meal2
        self.assertRaises(TypeError, wrong)

    def test_uncompatible(self):
        """Trying to set uncompatible type"""
        ep.start_session()
        meal1 = self.Meal.get(self.Meal.id == 1)
        def wrong():
            meal1.ingredients = 1
        self.assertRaises(TypeError, wrong)

