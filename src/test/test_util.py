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
        
    def test_queue(self):
        """Test the queue_iterator"""
        input = ['aa', 'ba', 'ab', 'bb', 'ac', 'bc']
        result = []
        for el in util.queue_iterator(input):
            if el[0] == 'a':
                input.append('x' + el)
            else:
                result.append(el)
                
        self.assertEqual(
            result, ['ba', 'bb', 'bc', 'xaa', 'xab', 'xac']
        )
            
        


if __name__ == "__main__":
    unittest.main()