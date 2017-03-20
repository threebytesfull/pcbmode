try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pcbmode.utils.gerber import gerberise, gerbers_to_svg, Gerber

class TestGerber(unittest.TestCase):
    """Test Gerber class"""

    def test_gerberise(self):
        pass

    def test_gerbers_to_svg(self):
        pass

    def test_gerber(self):
        pass
