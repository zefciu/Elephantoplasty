import os
import logging

from ConfigParser import SafeConfigParser
from psycopg2 import connect

import eplasty as ep

config_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../..',
    'test.ini',
)

config = SafeConfigParser()
config.read(config_file)
handler = logging.FileHandler('tests.log', 'w')
sql_logger = logging.getLogger('eplasty.queries.sql')
sql_logger.addHandler(handler)
err_logger = logging.getLogger('eplasty.errors')
err_logger.addHandler(handler)

def get_test_conn():
    
    return connect(
        host = config.get('db', 'host'),
        port = config.get('db', 'port'),
        database = config.get('db', 'database'),
        user = config.get('db', 'user'),
        password = config.get('db', 'password'),
        connection_factory=ep.cursor.EPConnection
    )
