try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pcbmode.utils.shape import Shape

class TestShape(unittest.TestCase):
    """Test Shape class"""

    def test_shape(self):
        pass
