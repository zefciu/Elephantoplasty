import unittest

import eplasty as ep
from eplasty import Object
from .util import get_test_conn

class Test(unittest.TestCase):
    """Tests for a simple tree"""

    def setUp(self):
        @ep.object.tree
        class Thing(Object):
            name = ep.field.CharacterVarying(30)

        self.connection = get_test_conn()
        ep.set_context(self.connection)
        animals = Thing(name='Animals')
        birds = Thing(name = 'Birds', parent=animals)
        mammals = Thing(name = 'Mammals', parent=animals)
        tiger = Thing(name = 'Tiger', parent=mammals)
        swallow = Thing(name = 'Swallow', parent=birds)
        european = Thing(name = 'European Swallow', parent=swallow)
        african = Thing(name = 'African Swallow', parent=swallow)
        ep.start_session()
        ep.add(animals, birds, mammals, tiger, swallow, european, african)
        ep.commit() 
        self.Thing = Thing

    def tearDown(self):
        c = ep.get_connection()
        c.cursor().execute('DROP TABLE things;')
        c.commit()

    def test_get(self):
        swallow = self.Thing.get(self.Thing.name == 'Swallow')
        self.assertEqual(
            set((child.name for child in swallow.children)),
            set(['European Swallow', 'African Swallow']),
        )
