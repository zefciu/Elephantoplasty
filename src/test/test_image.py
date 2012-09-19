import os
import unittest
import eplasty as ep
from .util import get_test_conn

try:
    import pystacia
except ImportError:
    pystacia = None

HERE = os.path.dirname(os.path.abspath(__file__))

@unittest.skipIf(pystacia is None, 'No pystacia, skipping imaging tests')
class Test(unittest.TestCase):

    def setUp(self):
        class Image(ep.Object):
            image = ep.f.Image()
            thumb = ep.f.Thumb(origin=image, size=(100, 100))

        self.Image = Image
        self.conn = get_test_conn()
        ep.set_context(self.conn)
        ep.start_session()
        img = pystacia.read(os.path.join(HERE, 'pythons.yotpeg'))
        img.filename = 'pythons.jpeg'
        pythons = Image(image=img)
        ep.add(pythons)
        ep.commit()

    def tearDown(self):
        self.conn.rollback()
        try:
            self.conn.cursor().execute('DROP TABLE images;')
            self.conn.commit()
        except ProgrammingError:
            pass

    def test_read(self):
        ep.start_session()
        pythons = self.Image.get(1)
        img = pythons.image
        thumb = pythons.thumb
        self.assertEqual(img.width, 640)
        self.assertEqual(thumb.width, 100)
