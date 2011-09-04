import unittest

from psycopg2 import ProgrammingError

from .util import get_test_conn
import eplasty as ep


class Test(unittest.TestCase):
    """Basic test for one-to-many relation"""

    def setUp(self):
        self.connection = get_test_conn()
        ep.set_context(self.connection)
        ep.start_session()

        class Ingredient(ep.Object):
            name = ep.f.CharacterVarying(20)

        class Meal(ep.Object):
            name = ep.f.CharacterVarying(20)
            ingredients = ep.rel.OneToMany(Ingredient, dependent=False)

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
            cur.execute('DROP TABLE ingredients;')
            cur.execute('DROP TABLE meals;')
            self.connection.commit()
        except ProgrammingError:
            pass

    def test_get_one(self):
        """Test if a single object gets correct set of children"""
        ep.start_session()
        meal = self.Meal.get(1)
        self.assertEqual(
            set([i.name for i in meal.ingredients]),
            set(['spam', 'bacon'])
        )

    def test_crude_remove(self):
        """Testing the behavior when we pop an element from list using ugly
        unpythonish syntax"""
        ep.start_session()
        meal = self.Meal.get(1)
        ing = meal.ingredients[0]
        self.assertEqual(ing.meal, meal)
        meal.ingredients = meal.ingredients[1:]
        self.assertEqual(ing.meal, None)

    def test_remove(self):
        """Testing the behavior when we pop an element from list"""
        ep.start_session()
        meal = self.Meal.get(1)
        ing = meal.ingredients[0]
        self.assertEqual(ing.meal, meal)
        meal.ingredients.pop(0)
        self.assertEqual(ing.meal, None)

    def test_non_dependent(self):
        """Test if the orphaned object persists"""
        ep.start_session()
        meal = self.Meal.get(1)
        ing = meal.ingredients[0]
        ing_id = ing.get_pk_value()
        meal.ingredients.pop(0)
        ep.commit()
        ep.start_session()
        ing2 = self.Ingredient.get(ing_id)
        self.assertEqual(ing2.meal, None)


if __name__ == "__main__":
    unittest.main()
