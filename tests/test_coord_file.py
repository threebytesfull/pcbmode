try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pcbmode.utils.coord_file

class TestCoordFile(unittest.TestCase):
    """Test makeCoordFile function"""

    def test_make_coord_file(self):
        pass
