import unittest
from eplasty import util


class Test(unittest.TestCase):


    def test_tname(self):
        """Test if the __table_name__ is set"""
        self.assertEqual(
            util.clsname2tname('RoundTableKnight'),
            'round_table_knights'
        )
        
    def test_tnamey(self):
        """Test the __table_name__ is set correcly when singular ends with y"""
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

    def test_diff_unsorted(self):
        """Test the diff_unsorted() method"""
        added, deleted = util.diff_unsorted(['a', 'b', 'c'], ['a', 'b', 'd'])
        self.assertEqual(added, ['d'])
        self.assertEqual(deleted, ['c'])

    def test_traceable_list(self):
        """Test the TraceableList object"""
        
        results = {}
        
        class SampleTraceableList(util.TraceableList):
            def callback(self, was, is_):
                results['was'] = was
                results['is_'] = is_
                
        s = SampleTraceableList([1, 2, 3, 4])
        s.pop()
        self.assertEqual(results, {'was': [1, 2, 3, 4], 'is_': [1, 2, 3]})

if __name__ == "__main__":
    unittest.main()
