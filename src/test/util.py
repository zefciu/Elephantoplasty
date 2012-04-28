import os
import logging

from configparser import ConfigParser
from psycopg2 import connect

import eplasty as ep

config_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../..',
    'test.ini',
)

config = ConfigParser()
config.read(config_file)
handler = logging.FileHandler('tests.log', 'w')
sql_logger = logging.getLogger('eplasty.queries.sql')
sql_logger.addHandler(handler)
err_logger = logging.getLogger('eplasty.errors')
err_logger.addHandler(handler)

def get_test_conn():
    
    return connect(
        host = config['db']['host'],
        port = config['db']['port'],
        database = config['db']['database'],
        user = config['db']['user'],
        password = config['db']['password'],
        connection_factory=ep.cursor.EPConnection
    )
