import unittest
from unittest.mock import patch

from pcbmode.utils.style import Style
from pcbmode.config import Config

class TestStyle(unittest.TestCase):
    """Test Style module"""

    def test_style(self):
        c = Config()
        c.load_defaults()
        style = Style({}, 'conductor')
