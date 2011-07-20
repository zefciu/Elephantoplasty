'''
Created on Jun 7, 2011

@author: szymon
'''
import unittest
from eplasty.ctx import del_context, set_context, get_cursor, CtxError, connect
from eplasty.ctx import get_connection, commit, add, get_session
from .util import get_test_conn, config
from psycopg2.extensions import cursor
from eplasty.session import Session

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        del_context()


    def test_set_with_connection(self):
        set_context(get_test_conn())
        get_cursor() #Passes when no error
        
    def test_set_with_cursor(self):
        set_context(get_test_conn().cursor())
        get_cursor() #Passes when no error
        
    def test_unset_connection(self):
        self.assertRaises(CtxError, get_cursor)
        
    def test_connect(self):
        connect(
            host = config.get('db', 'host'),
            port = config.get('db', 'port'),
            database = config.get('db', 'database'),
            user = config.get('db', 'user'),
            password = config.get('db', 'password'),
        )
        get_cursor() #Passes when no error
        
    def test_get_connection_simple(self):
        """Passing a connection to get_connection should return itself"""
        conn = get_test_conn()
        self.assertEqual(conn, get_connection(conn))
        
    def test_no_connection(self):
        """Behavior when no context present"""
        self.assertRaises(CtxError, lambda: get_connection())
        self.assertRaises(CtxError, lambda: get_cursor())
        self.assertRaises(CtxError, lambda: get_session())
        self.assertRaises(CtxError, lambda: commit())
        self.assertRaises(CtxError, lambda: add())
        
    def test_invalid_context(self):
        """Set context with invalid value"""
        self.assertRaises(TypeError, lambda: set_context(1))
        
    def test_get_cursor_with_conn(self):
        """Get cursor for connection"""
        self.assertEqual(type(get_cursor(get_test_conn())), cursor)
        
    def test_get_cursor_with_cursor(self):
        """Passing a cursor to get_cursor should return itself"""
        cur = get_test_conn().cursor()
        self.assertEqual(get_cursor(cur), cur)
        
    def test_get_cursor_with_invalid(self):
        """Passing invalid type to get_cursor"""
        self.assertRaises(TypeError, lambda: get_cursor(1))
        
    def test_get_session_with_session(self):
        """Passing a session to get_session() should return itself"""
        session = Session(get_test_conn())
        self.assertEqual(get_session(session), session)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()