import unittest

from eplasty.query import SelectQuery

class Test(unittest.TestCase):
    """Various tests for query objects"""
    
    def test_simplest(self):
        """Test a simplest query"""
        s = SelectQuery('foobars')
        self.assertEqual(s.render(), ('SELECT * FROM foobars WHERE 1 = 1;',()))
