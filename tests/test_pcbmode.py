try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pcbmode import pcbmode

class TestPcbmode(unittest.TestCase):
    """Test pcbmode script"""

    def test_pcbmode(self):
        pass
