'''
Testing the exception raising of various objects and methods
'''
import unittest
from eplasty.table import Table


class Test(unittest.TestCase):


    def test_virtual_table(self):
        """Trying to get an instance of a table with no columns"""
        class Abs(Table):
            pass
        self.assertRaises(NotImplementedError, lambda: Abs())


if __name__ == "__main__":
    unittest.main()