import os
from configparser import SafeConfigParser
from psycopg2 import connect

config_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../..',
    'test.ini',
)

config = SafeConfigParser()
config.read(config_file)

def get_test_conn():
    return connect(
        host = config.get('db', 'host'),
        port = config.get('db', 'port'),
        database = config.get('db', 'database'),
        user = config.get('db', 'user'),
        password = config.get('db', 'password'),
    )
