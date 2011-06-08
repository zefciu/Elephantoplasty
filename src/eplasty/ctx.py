"""Things related to the global context"""
from psycopg2.extensions import cursor, connection
from eplasty.session import Session
import psycopg2

class CtxError(StandardError):
    """Exception raised on problems with context"""
    
class Ctx(object):
    """This class will have one global instance - the default context"""
    __slots__ = ['connection', 'cursor', 'session']
    
    def __init__ (self, connection = None, cursor = None):
        self.connection = connection
        self.cursor = cursor
        
ctx = Ctx()

def connect(*args, **kwargs):
    """
Passes all arguments to psycopg2 ``connect`` and creates a connection in global
context.
    """
    global ctx
    del_context()
    ctx.connection = psycopg2.connect(*args, **kwargs)

def get_connection(arg = None):
    """
Get a connection. Will return the argument or try to find connection in context
    """
    global ctx
    if arg:
        return arg
    elif ctx.connection:
        return ctx.connection
    else:
        raise CtxError, 'No connection passed and no in global context'
    
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
    
    global ctx
    
    if arg:
        if isinstance(arg, cursor):
            return arg
        elif isinstance(arg, connection):
            return arg.cursor()
        else:
            raise TypeError, 'Context must be a connection or a cursor'
    else:
        if ctx.cursor:
            return ctx.cursor
        elif ctx.connection:
            cur = ctx.connection.cursor()
            ctx.cursor = cur
            return cur
        else:
            raise CtxError, 'No context available to create a cursor'

def set_context(arg):
    """Set a global context using a connection or cursor"""
    global ctx
    
    if isinstance(arg, connection):
        ctx.connection = arg
    elif isinstance(arg, cursor):
        ctx.connection = arg.connection
        ctx.cursor = arg
    else:
        raise (
            TypeError,
            'Context must be a connection or a cursor, not {0}'.format(
                type(arg)
            )
        )
        
def del_context():
    """Clear the global context"""
    global ctx
    
    ctx.connection = None
    ctx.cursor = None

def start_session():
    """Start the session in global context"""
    global ctx
    ctx.session = Session(get_connection())
    
def is_global_session():
    """Check if global session exists and return it or false""" 
    global ctx
    return ctx.session or False
    