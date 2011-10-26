import unittest

from psycopg2 import ProgrammingError

from .util import get_test_conn
import eplasty as ep

from eplasty.object.exc import NotFound
from eplasty.object.const import ORPHANED

class Test(unittest.TestCase):
    """Variations on one2many with dependent child class"""

    def setUp(self):
        self.connection = get_test_conn()
        ep.set_context(self.connection)
        ep.start_session()

        class Ingredient(ep.Object):
            name = ep.f.CharacterVarying(20)

        class Meal(ep.Object):
            name = ep.f.CharacterVarying(20)
            ingredients = ep.rel.OneToMany(Ingredient, dependent=True)

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

    def test_dependent(self):
        """Test if the orphaned object is removed"""
        ep.start_session()
        meal = self.Meal.get(1)
        ing = meal.ingredients[0]
        ing_id = ing.get_pk_value()
        meal.ingredients.pop(0)
        self.assertEqual(ing._status, ORPHANED)
        ep.commit()
        ep.start_session()
        def wrong():
            return self.Ingredient.get(ing_id)
        self.assertRaises(NotFound, wrong)

    def test_move(self):
        """Test if you can safely move a dependent object without it getting
        deleted"""
        ep.start_session()
        meal1 = self.Meal.get(1)
        meal2 = self.Meal.get(2)
        ing = meal1.ingredients.pop(0)
        ing_id = ing.id
        meal2.ingredients.append(ing)
        ep.commit()
        ep.start_session()
        meal1 = self.Meal.get(1)
        meal2 = self.Meal.get(2)
        ing = self.Ingredient.get(ing_id)
        self.assertEqual(len(meal1.ingredients), 1)
        self.assertEqual(len(meal2.ingredients), 4)
