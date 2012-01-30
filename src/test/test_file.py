try:
    import unittest2 as unittest
except ImportError:
    import unittest

import eplasty as ep

from .util import get_test_conn

CONTENT = 'Lorem ipsum dolor sit amet'

class Test(unittest.TestCase):
    """Tests for FileField"""

    def setUp(self):
        class Skit(ep.Object):
            title = ep.f.CharacterVarying(length=16)
            content = ep.f.FileField()

        Skit.create_table()
        self.conn = get_test_conn()
        ep.set_context(self.conn)
        ep.start_session()
        self.Skit = Skit
        parrot = Skit(title='parrot')
        ep.add(parrot)
        parrot.content.write(CONTENT)
        ep.commit()

    def tearDown(self):
        self.conn.rollback()
        self.conn.cursor().execute('DROP TABLE skits;')
        self.conn.commit()

    def test_read(self):
        ep.start_session()
        parrot = self.Skit.get(1)
        content = parrot.content.read()
        self.assertEqual(content, CONTENT)
