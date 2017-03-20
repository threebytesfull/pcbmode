try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pcbmode.utils.place import placeShape, placeDrill

class TestPlace(unittest.TestCase):
    """Test place functions"""

    def test_place_shape(self):
        pass

    def test_place_drill(self):
        pass
