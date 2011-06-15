import unittest
from eplasty import util


class Test(unittest.TestCase):


    def test_tname(self):
        self.assertEqual(
            util.clsname2tname('RoundTableKnight'),
            'round_table_knights'
        )
        
    def test_tnamey(self):
        self.assertEqual(
            util.clsname2tname('BitterCherry'),
            'bitter_cherries'
        )
        


if __name__ == "__main__":
    unittest.main()