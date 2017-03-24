try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pcbmode.utils.excellon import makeExcellon, Excellon

class TestExcellon(unittest.TestCase):
    """Test Excellon module"""

    def test_make_excellon(self):
        pass

    def test_excellon(self):
        pass
