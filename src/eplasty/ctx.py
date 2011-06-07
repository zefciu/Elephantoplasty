"""Things related to the global context"""
from psycopg2.extensions import cursor, connection

class CtxError(StandardError):
    """Exception raised on problems with context"""
    
class Ctx(object):
    """This class will have one global instance - the default context"""
    __slots__ = ['connection', 'cursor']
    
    def __init__ (self, connection = None, cursor = None):
        self.connection = connection
        self.cursor = cursor
        
ctx = Ctx()

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

