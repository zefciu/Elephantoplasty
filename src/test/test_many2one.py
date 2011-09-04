import unittest

from psycopg2 import ProgrammingError

from eplasty import Object
from eplasty.field import CharacterVarying
from eplasty.relation import ManyToOne
from test.util import get_test_conn
from eplasty.ctx import set_context, start_session, add, commit


class Test(unittest.TestCase):
    """Basic tests for many-to-one relationships"""

    def setUp(self):

        class Movie(Object):
            title = CharacterVarying(30)

        class Character(Object):
            name = CharacterVarying(30)
            movie = ManyToOne(Movie)

        self.connection = get_test_conn()
        set_context(self.connection)
        start_session()
        life = Movie(title = 'Life of Brian')
        grail = Movie(title = 'MP & the Holy Grail')
        add(life)
        add(grail)
        for c in [
            ('Brain', life),
            ('Patsy', grail),
            ('Arthur', grail),
        ]:
            name, movie = c
            char = Character(name = name, movie = movie)
            add(char)
            
        commit()

        self.Character = Character
        self.Movie = Movie


    def tearDown(self):
        cur = self.connection.cursor()
        try:
            cur.execute('DROP TABLE characters CASCADE;')
            cur.execute('DROP TABLE movies CASCADE;')
            self.connection.commit()
        except ProgrammingError:
            pass
            

    def test_get(self):
        start_session()
        c = self.Character.get(name = 'Patsy')
        self.assertEqual(c.movie.title, 'MP & the Holy Grail')


if __name__ == "__main__":
    unittest.main()
