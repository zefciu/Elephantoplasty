"""Psycopg cursor and conection classes augmented with logging"""
import logging

import psycopg2

class EPCursor(psycopg2.extensions.cursor):
    """Custom cursor class that performs logging"""

    def __init__(self, *args, **kwargs):
        # self.unad_logger = logging.getLogger('eplasty.queries.unadapted')
        self.sql_logger = logging.getLogger('eplasty.queries.sql')
        self.err_logger = logging.getLogger('eplasty.errors')
        super(EPCursor, self).__init__(*args, **kwargs)

    def execute(self, sql, args=None):
        #self.unad_logger.info(sql)
        #self.unad_logger.info(args)
        try:
            command = self.mogrify(sql, args)
            self.sql_logger.info(command)
            super(EPCursor, self).execute(command)
        except Exception as exc:
            self.err_logger.error(exc)
            raise

class EPConnection(psycopg2.extensions.connection):
    """Connection class that creates logging cursors"""

    def __init__(self, *args, **kwargs):
        result =  super(EPConnection, self).__init__(*args, **kwargs)
        self.save()
        return result

    def cursor(self, *args, **kwargs):
        kwargs.setdefault('cursor_factory', EPCursor)
        return super(EPConnection, self).cursor(*args, **kwargs)

    def save(self):
        """Sets a savepoint to which this connection should be rolled
        back if a EAFP error appears. This should be used if some data is
        stored in this connection which can be lost on EAFP rollback"""
        self.cursor().execute('SAVEPOINT clean;')
        self.savepoint = 'clean'

    def rollback_clean(self):
        self.cursor().execute(
            'ROLLBACK TO SAVEPOINT {0};'.format(self.savepoint)
        )
