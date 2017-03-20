try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pcbmode.utils.module import Module

class TestModule(unittest.TestCase):
    """Test Module class"""

    def test_module(self):
        pass
