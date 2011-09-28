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
            ('Brian', life),
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
        """Most basic test of finding related object"""
        start_session()
        c = self.Character.get(self.Character.name == 'Patsy')
        self.assertEqual(c.movie.title, 'MP & the Holy Grail')

    def test_backref(self):
        """Testing if backref is correctly created"""
        grail = self.Movie.get(self.Movie.title == 'MP & the Holy Grail')
        self.assertEqual(
            set((character.name for character in grail.characters)),
            set(['Patsy', 'Arthur'])
        )

    def test_find_by_related(self):
        """Test finding by related object"""
        start_session()
        life = self.Movie.get(self.Movie.title == 'Life of Brian')
        characters = self.Character.find(self.Character.movie == life)
        self.assertEqual(list(characters)[0].name, 'Brian')


if __name__ == "__main__":
    unittest.main()
