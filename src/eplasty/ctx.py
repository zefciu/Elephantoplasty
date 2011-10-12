"""Things related to the global context"""
import threading

import psycopg2
from psycopg2.extensions import cursor, connection

from eplasty.session import Session
from eplasty.cursor import EPConnection

class CtxError(Exception):
    """Exception raised on problems with context"""
    
class Ctx(threading.local):
    """Thread-local class with default context"""
    
    def __init__ (self, connection_ = None, cursor_ = None, session = None):
        super(Ctx, self).__init__()
        self.connection = connection_
        self.cursor = cursor_
        self.session = session
     
ctx = Ctx()

def connect(*args, **kwargs):
    """
Passes all arguments to psycopg2 ``connect`` and creates a connection in global
context.
    """
    del_context()
    kwargs.setdefault('connection_factory', EPConnection)
    ctx.connection = psycopg2.connect(*args, **kwargs)

def get_connection(arg = None):
    """
Get a connection. Will return the argument or try to find connection in context
    """
    if arg:
        return arg
    elif ctx.connection:
        return ctx.connection
    else:
        raise CtxError('No connection passed and no in global context')
    
def get_cursor(arg = None):
    """Get a cursor. Will try do create it in the following way:
    * If a cursor is provided as argument - returns it
    * If a connection is provided as argument - creates a cursor for this
      connection
    * If there is no argument given - checks the global ctx object for cursor
    * If there is no cursor in the global ctx, but there is connection, creates
      a cursor, places it in ctx and returns it
    * If there is neither given nor global context, raise CtxError
    """
    
    
    if arg:
        if isinstance(arg, cursor):
            return arg
        elif isinstance(arg, connection):
            return arg.cursor()
        else:
            raise TypeError('Context must be a connection or a cursor')
    else:
        if ctx.cursor:
            return ctx.cursor
        elif ctx.connection:
            cur = ctx.connection.cursor()
            ctx.cursor = cur
            return cur
        else:
            raise CtxError('No context available to create a cursor')

def set_context(arg):
    """Set a global context using a connection or cursor"""
    
    if isinstance(arg, connection):
        ctx.connection = arg
    elif isinstance(arg, cursor):
        ctx.connection = arg.connection
        ctx.cursor = arg
    else:
        raise TypeError
        
def del_context():
    """Clear the global context"""
    
    ctx.connection = None
    ctx.cursor = None
    ctx.session = None

def start_session():
    """Start the session in global context"""
    if ctx.session:
        ctx.session.close()
    ctx.session = Session(get_connection())
    
def commit():
    """Commit the global session"""
    if ctx.session:
        ctx.session.commit()
    else:
        raise CtxError('No session in global context')
    
def add(*args, **kwargs):
    """Add to global session"""
    if ctx.session:
        ctx.session.add(*args, **kwargs)
    else:
        raise CtxError('No session in global context')
        

def is_global_session():
    """Check if global session exists and return it or false""" 
    return ctx.session or False
    
def get_session(session_ = None):
    """Return its argument or global session. If neither is present, raise
    CtxError"""
    if session_:
        return session_
    session_ = is_global_session()
    if session_:
        return session_
    raise CtxError('Cannot find a session')
