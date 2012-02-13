try:
    import unittest2 as unittest
except ImportError:
    import unittest
from psycopg2 import OperationalError

import eplasty as ep

from .util import get_test_conn

CONTENT = 'Lorem ipsum dolor sit amet'

class Test(unittest.TestCase):
    """Tests for FileField"""

    def setUp(self):
        class Skit(ep.Object):
            title = ep.f.CharacterVarying(length=16)
            content = ep.f.FileField()

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
        """Simple test for reading a lobject content"""
        ep.start_session()
        parrot = self.Skit.get(1)
        content = parrot.content.read()
        self.assertEqual(content, CONTENT)

    def test_delete(self):
        """Check if no garbage is left after we delete object containg lobject
        """
        ep.start_session()
        parrot = self.Skit.get(1)
        oid = parrot.content.oid
        parrot.delete()
        ep.commit()
        self.assertRaises(OperationalError, lambda: self.conn.lobject(oid))

    def test_unlink(self):
        """Check if unlinking an lobject is handled by None'ing a field"""
        ep.start_session()
        parrot = self.Skit.get(1)
        parrot.content.unlink()
        ep.commit()
        ep.start_session()
        parrot = self.Skit.get(1)
        self.assertEqual(parrot.content.read(), '')

