import unittest

from eplasty.query import SelectQuery
from eplasty.conditions import Equals

class Test(unittest.TestCase):
    """Various tests for query objects"""
    
    def test_simplest(self):
        """Test a simplest query"""
        s = SelectQuery('eggs')
        self.assertEqual(s.render(), ('SELECT * FROM eggs WHERE 1 = 1;',()))

    def test_with_columns(self):
        """Test a simplest query"""
        s = SelectQuery('eggs', columns=['id', 'name'])
        self.assertEqual(
            s.render(),
            ('SELECT id, name FROM eggs WHERE 1 = 1;',())
        )

    def test_joins(self):
        """Test if joins are rendered"""
        s = SelectQuery('eggs', joins=[
            ('LEFT', 'sausages', 'sausages.egg_id', 'eggs.id')
        ])
        self.assertEqual(
            s.render(),
            ('SELECT * FROM eggs LEFT JOIN sausages ON sausages.egg_id = '
            'eggs.id WHERE 1 = 1;',())
        )
