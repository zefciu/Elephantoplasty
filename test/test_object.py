import unittest

import eplasty
from eplasty import field

class Bird(eplasty.Object):
    """Test object"""
    species = field.Char()
    voltage = field.Integer()

class TestObject(unittest.TestCase):
    """Tests of EP object"""

    def test_read(self):
        """Test if data in tuple is correctly read"""
        o = Bird.from_tuple(("parrot", 1e6))
        self.assertEqual(o.species, "parrot")
        self.assertEqual(o.voltage, 1e6)

    def test_write(self):
        """Test if data is stored in the tuple"""
        o = Bird()
        o.species = "parrot"
        o.voltage = 1e6
        self.assertListEqual(o.__list__, ["parrot", 1e6])
