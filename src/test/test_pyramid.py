import unittest

from eplasty import field as f
from eplasty import Object
from eplasty.ctx import set_context, start_session, commit, add, get_connection
from .util import get_test_conn
from eplasty.object import NotFound, TooManyFound
from eplasty.object.exc import LifecycleError

try:
    from pyramid_eplasty.traverser import Traverser
except ImportError:
    Traverser = None

class Root(dict):
    __parent__ = None
    __name__ = ''


@unittest.skipIf(Traverser is None, 'No pyramid_eplasty, skipping tests')
class Test(unittest.TestCase):
    """Optional tests for pyramid_eplasty package"""

    def setUp(self):
        
        class Knight(Object):
            title = f.CharacterVarying(
                length = 5, null = False, default = 'Sir'
            )
            name = f.CharacterVarying(length = 20, null = False)
            nickname = f.CharacterVarying(length = 20, null = True)
            score = f.Integer()
            
        self.Knight = Knight
        self.root = Root()
        Traverser(self.Knight, 'name').mount(self.root, 'knights')
        set_context(get_test_conn())
        start_session()
        # Knight.create_table()
        
        for ktup in [
            ('Sir', 'Galahad', 'The Pure', 10),
            ('King', 'Arthur', None, 20),
            ('Sir', 'Robin', 'The Brave', 30),
            ('Sir', 'Lancelot', None, 40),
        ]:
            title, name, nickname, score = ktup
            k = Knight(
                title = title,
                name = name,
                nickname = nickname,
                score = score
            )
            add(k)
            
        commit()
        start_session()

    def tearDown(self):
        c = get_connection()
        c.cursor().execute('DROP TABLE knights;')
        c.commit()

    def test_get(self):
        knight = self.root['knights']['Galahad']
        self.assertEqual(knight.title, 'Sir')
        self.assertEqual(knight.name, 'Galahad')
        self.assertEqual(knight.nickname, 'The Pure')
        self.assertEqual(knight.score, 10)


