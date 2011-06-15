'''
Various utilities.
'''

import re

CAPITAL = re.compile('[A-Z]')

def clsname2tname(clsname):
    """Transforms the class name into default table name"""
    first = clsname[0].lower()
    rest = clsname[1:]
    sing = first + re.sub(CAPITAL, lambda x: '_' + x.group(0).lower(), rest)
    if sing[-1] == 'y':
        return sing[:-1] + 'ies'
    else:
        return sing + 's'
    
    
    
    
    
