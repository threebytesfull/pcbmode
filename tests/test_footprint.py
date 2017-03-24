try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pcbmode.utils.footprint import Footprint

class TestFootprint(unittest.TestCase):
    """Test Footprint class"""

    def test_footprint(self):
        pass
