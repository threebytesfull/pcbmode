import unittest
from unittest.mock import patch

from pcbmode.utils.style import Style
from pcbmode.config import Config

class TestStyle(unittest.TestCase):
    """Test Style module"""

    def setUp(self):
        self.c = Config(clean=True)

    def test_style(self):
        self.c.load_defaults()
        style = Style({'type': 'rect'}, 'conductor')
