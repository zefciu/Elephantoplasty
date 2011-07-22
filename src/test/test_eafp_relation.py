from psycopg2 import ProgrammingError

import unittest
import eplasty as ep
from test.util import get_test_conn


class Test(unittest.TestCase):
    """
    Just one special test
    """


    def test_eaft_relation(self):
        """
        This is a special test to create a related table when object depending
        on it (but with foreign key = NULL) is flushed
        """

        class Movie(ep.Object):
            title = ep.f.CharacterVarying(30)

        class Character(ep.Object):
            name = ep.f.CharacterVarying(30)
            movie = ep.rel.ManyToOne(Movie)

        c = Character(name="Nobody important", movie = None)

        self.connection = get_test_conn()
        ep.set_context(self.connection)
        ep.start_session()

        ep.add(c)
        ep.commit()
        
    
    def tearDown(self):
        self.connection.rollback()
        cur = self.connection.cursor()
        try:
            cur.execute('DROP TABLE movies CASCADE;')
            cur.execute('DROP TABLE characters;')
            self.connection.commit()
        except ProgrammingError:
            pass


if __name__ == "__main__":
    unittest.main()