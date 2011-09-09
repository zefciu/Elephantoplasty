'''
Created on Jun 9, 2011

@author: szymon
'''
import unittest
from eplasty.conditions import Equals, And


class Test(unittest.TestCase):


    def test_equals(self):
        c = Equals('score', 3)
        self.assertEqual(c.render(), ('score = %s', (3,)))
        
    def test_and(self):
        """Testing AND as class"""
        x = Equals('name', 'Sir Lancelot')
        y = Equals('score', 3)
        self.assertEqual(
            And(x, y).render(),
            ('(name = %s) AND (score = %s)', ('Sir Lancelot', 3))
        )

    def test_and_operator(self):
        """Testing AND as operator"""
        x = Equals('name', 'Sir Lancelot')
        y = Equals('score', 3)
        self.assertEqual(
            (x & y).render(),
            ('(name = %s) AND (score = %s)', ('Sir Lancelot', 3))
        )
        


if __name__ == "__main__":
    unittest.main()
