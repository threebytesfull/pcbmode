try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pcbmode.utils.bom

class TestBom(unittest.TestCase):
    """Test make_bom function"""

    def test_make_bom(self):
        pass
