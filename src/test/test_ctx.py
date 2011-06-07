'''
Created on Jun 7, 2011

@author: szymon
'''
import unittest
from eplasty.ctx import del_context, set_context, get_cursor, CtxError
from util import get_connection


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        del_context()


    def test_set_with_connection(self):
        set_context(get_connection())
        get_cursor() #Passes when no error
        
    def test_set_with_cursor(self):
        set_context(get_connection().cursor())
        get_cursor() #Passes when no error
        
    def test_unset_connection(self):
        self.assertRaises(CtxError, get_cursor)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()