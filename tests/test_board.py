import unittest
from unittest.mock import patch

from pcbmode.utils.board import Board
from pcbmode.config import Config

class TestBoard(unittest.TestCase):
    """Test pcbmode script"""

    def setUp(self):
        self.c = Config(clean=True)

    @patch('pcbmode.utils.board.Module')
    def test_board_instantiates_module(self, mock_module):
        """
        When a Board object is created, it instantiates a Module object. It
        looks like it doesn't actually need to store references to the config
        as they're not used anywhere else. These can probably be removed...
        """
        board = Board()
        self.assertTrue(mock_module.called, 'Board should instantiate a Module')
        self.assertTrue(hasattr(board, '_module_dict'), 'board should have protected module_dict attribute')
        self.assertTrue(hasattr(board, '_module_routing'), 'board should have protected module_routing attribute')

        self.assertIs(board._module_dict, self.c.get('brd'), 'module_dict attribute should be same object as config.brd')
        self.assertIs(board._module_routing, self.c.get('rte'), 'module_routing attribute should be same object as config.rte')
