try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pcbmode.utils.extract

class TestExtract(unittest.TestCase):
    """Test extraction methods"""

    def test_extract(self):
        pass

    def test_extract_components(self):
        pass

    def test_extract_routing(self):
        pass

    def test_extract_refdefs(self):
        pass

    def test_extract_docs(self):
        pass
