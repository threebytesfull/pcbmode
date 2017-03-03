import unittest
from unittest.mock import patch

from pcbmode import config

class TestConfig(unittest.TestCase):
    """Test config dictionary"""

    def test_config_dict_entries(self):
        expected_keys = 'cfg brd stl pth msg stk'.split()
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertTrue(hasattr(config, key), 'config should contain {} dict'.format(key))
