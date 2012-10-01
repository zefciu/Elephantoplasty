import unittest

from eplasty import field as f
from eplasty import Object
from eplasty.ctx import set_context, start_session, commit, add, get_connection
from .util import get_test_conn

class Test(unittest.TestCase):
    """Testing pagination."""

    def setUp(self):
        
        class Knight(Object):
            name = f.CharacterVarying(length = 20, null = False)

        self.Knight = Knight
        set_context(get_test_conn())
        start_session()

        for knight_name in [
            'Agravain', 'Bagdemagus', 'Bedivere', 'Bors', 'Breunor',
            'Calogrenant', 'Caradoc', 'Dagonet', 'Dinadan', 'Gaheris',
            'Galahad', 'Gareth', 'Gawain', 'Geraint', 'Griflet',
            'Hector de Maris', 'Kay', 'Lamorak', 'Lancelot', 'Leodegrance',
            'Lionel', 'Lucan', 'Maleagant', 'Marhaus', 'Palamedes', 'Pelleas',
            'Pellinore', 'Percival', 'Safir', 'Sagramore', 'Segwarides', 'Tor',
        ]: # There are 32 knights
            knight = Knight(name=knight_name)
            add(knight)
        commit()

    def tearDown(self):
        c = get_connection()
        c.rollback()
        c.cursor().execute('DROP TABLE knights;')
        c.commit()

    def test_no_widow(self):
        """Testing the behaviour without widow control."""
        pager = self.Knight.paginate(page_size=10)
        self.assertEqual(pager.get_page_count(), 4)
        self.assertEqual(len(list(pager.get_page(1))), 10)
        self.assertEqual(len(list(pager.get_page(2))), 10)
        self.assertEqual(len(list(pager.get_page(3))), 10)
        self.assertEqual(len(list(pager.get_page(4))), 2)
        self.assertEqual(len(list(pager.get_page(5))), 0)

    def test_widow_control(self):
        """Testing the behaviour with widow control."""
        pager = self.Knight.paginate(page_size=10, widow_size=2)
        self.assertEqual(pager.get_page_count(), 3)
        self.assertEqual(len(list(pager.get_page(1))), 10)
        self.assertEqual(len(list(pager.get_page(2))), 10)
        self.assertEqual(len(list(pager.get_page(3))), 12)
        self.assertEqual(len(list(pager.get_page(4))), 0)
