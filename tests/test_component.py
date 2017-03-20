try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pcbmode.utils.component import Component

class TestComponent(unittest.TestCase):
    """Test Component classs"""

    def test_component(self):
        pass
