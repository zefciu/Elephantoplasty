try:
    import unittest2 as unittest
except ImportError:
    import unittest
from psycopg2 import OperationalError

import eplasty as ep

from .util import get_test_conn

CONTENT_PARROT = 'Lorem ipsum dolor sit amet'
CONTENT_HUNGARIAN = 'Lorem ipsum dolor sit amet'
CONTENT_INQUISITION = 'Lorem ipsum dolor sit amet'

class Test(unittest.TestCase):
    """Tests for FileField"""

    def setUp(self):
        class Skit(ep.Object):
            title = ep.f.CharacterVarying(length=16)
            content = ep.f.FileField()

        class Jpeg(ep.Object):
            title = ep.f.CharacterVarying(length=16)
            content = ep.f.FileField(mimetype='image/jpeg')

        self.Skit = Skit
        self.Jpeg = Jpeg
        self.conn = get_test_conn()
        ep.set_context(self.conn)
        ep.start_session()
        parrot = Skit(title='parrot')
        ep.add(parrot)
        parrot.content.filename='parrot.txt'
        parrot.content.write(CONTENT_PARROT)
        hungarian = Skit(title='hungarian')
        ep.add(hungarian)
        hungarian.content.filename='hungarian.txt'
        hungarian.content.mimetype='text/x-rst'
        hungarian.content.write(CONTENT_HUNGARIAN)
        img = Jpeg(title='pythons')
        ep.add(img)
        img.content.export('pythons.yotpeg')
        inquisition = Skit(title='inquisition')
        ep.add(inquisition)
        inquisition.content.filename='inquisition'
        inquisition.content.write(CONTENT_INQUISITION)
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
        self.assertEqual(content, CONTENT_PARROT)

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

    def test_size(self):
        """Test getting the size. As it involves seek()ing also check if
        position is unchanged"""
        ep.start_session()
        parrot = self.Skit.get(1)
        parrot.content.seek(10)
        self.assertEqual(parrot.content.get_size(), len(CONTENT_PARROT))
        self.assertEqual(parrot.content.tell(), 10)

    def test_mime(self):
        ep.start_session()
        parrot = self.Skit.get(1)
        self.assertEqual(parrot.content.filename, 'parrot.txt')
        self.assertEqual(parrot.content.mimetype, 'text/plain')

    def test_forced_mime(self):
        ep.start_session()
        hungarian = self.Skit.get(2)
        self.assertEqual(hungarian.content.filename, 'hungarian.txt')
        self.assertEqual(hungarian.content.mimetype, 'text/x-rst')

    def test_fixed_mime(self):
        ep.start_session()
        pythons = self.Jpeg.get(1)
        self.assertEqual(pythons.content.filename, 'pythons.yotpeg')
        self.assertEqual(pythons.content.mimetype, 'image/jpeg')
        def broken():
            pythons.content.mimetype = 'image/png'
        self.assertRaises(AttributeError, broken)
        
    def test_no_mime(self):
        ep.start_session()
        inquisition = self.Skit.get(3)
        self.assertEqual(
            inquisition.content.mimetype, 'application/octet-stream'
        )

    def test_assigment(self):
        ep.start_session()
        inquisition = self.Skit.get(3)
        def broken():
            inquisition.content = 'xxx'
        self.assertRaises(AttributeError, broken)

    def test_not_added(self):
        parrot2 = self.Skit(title='parrot2')
        def broken():
            parrot2.content.write(CONTENT_PARROT)
        self.assertRaises(ep.object.exc.LifecycleError, broken)

