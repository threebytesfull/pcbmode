try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import io
import pyparsing as PP

from pcbmode.config import Config
from pcbmode.utils.svgpath import SvgPath

class TestSvgPath(unittest.TestCase):
    """Test SvgPath module"""

    def setUp(self):
        self.c = Config(clean=True)
        self.c.load_defaults()

    @unittest.skip('current parser fails with empty string')
    def test_svg_path_from_empty_string(self):
        """A path with no commands is valid according to the SVG spec"""
        path = SvgPath('')

    def test_svg_path_from_invalid_string(self):
        """A path with an unknown command should raise a parsing exception"""
        with self.assertRaises(Exception):
            path = SvgPath('F9 9 9')

    @patch('pcbmode.utils.svgpath._make_svg_grammar')
    def test_would_notify_unhandled_but_parsed_command_in_make_relative(self, grammar_method):
        """If the parser matched an element not handled in the if statements, it should be notified at the bottom"""
        fake_grammar = PP.Group(PP.Literal('B') + PP.Group(PP.Word('12345') * 2))
        grammar_method.return_value = fake_grammar
        with self.assertRaises(Exception):
            with patch('sys.stdout', new=io.StringIO()) as fake_out:
                path = SvgPath('B 234 567')
                self.assertEqual(fake_out.getValue(), 'ERROR: found an unsupported SVG path command B')
            # it will go on to fail later, so just ignore that

    def assertPathParses(self, svg_string, expected_results):
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        if 'first_point' in expected_results:
            self.assertEqual(path.getFirstPoint(), expected_results['first_point'], 'getFirstPoint should return first move point')
        if 'width' in expected_results:
            self.assertEqual(path.getWidth(), expected_results['width'], 'should calculate correct width')
        if 'height' in expected_results:
            self.assertEqual(path.getHeight(), expected_results['height'], 'should calculate correct height')
        if 'num_segments' in expected_results:
            self.assertEqual(path.getNumberOfSegments(), expected_results['num_segments'], 'should get correct number of segments')
        return path

    def test_svg_path_from_same_svg_string(self):
        svg_string = 'M 9 8'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        path2 = SvgPath(svg_string)
        self.assertIs(path.getFirstPoint(), path2.getFirstPoint(), 'should get same path first point object')

    def test_svg_path_from_move_single(self):
        self.assertPathParses('M 1 2', {
            'first_point': ['1', '2'],
            'width': 0,
            'height': 0,
            'num_segments': 1,
            })

    def test_svg_path_from_move_single_relative(self):
        self.assertPathParses('m 1 2', {
            'first_point': ['1', '2'],
            'width': 0,
            'height': 0,
            'num_segments': 1,
            })

    def test_svg_path_from_move_multi(self):
        self.assertPathParses('M 1 2 3 4', {
            'first_point': ['1', '2'],
            'width': 2,
            'height': 2,
            'num_segments': 1,
            })

    def test_svg_path_from_move_multi_relative(self):
        self.assertPathParses('m 1 2 3 4', {
            'first_point': ['1', '2'],
            'width': 3,
            'height': 4,
            'num_segments': 1,
            })
        svg_string = 'm 1 2 3 4'

    def test_svg_path_from_moves_single(self):
        self.assertPathParses('M 1 2 M 3 4', {
            'first_point': ['1', '2'],
            'width': 2,
            'height': 2,
            'num_segments': 2,
            })
        # first move being relative should make no difference
        self.assertPathParses('m 1 2 M 3 4', {
            'first_point': ['1', '2'],
            'width': 2,
            'height': 2,
            'num_segments': 2,
            })

    def test_svg_path_from_moves_single_relative(self):
        self.assertPathParses('M 1 2 m 3 4', {
            'first_point': ['1', '2'],
            'width': 3,
            'height': 4,
            'num_segments': 2,
            })

    def test_svg_path_from_vertical_line_single(self):
        self.assertPathParses('M3-2V5', {
            'first_point': ['3', '-2'],
            'width': 0,
            'height': 7,
            'num_segments': 1,
            })

    def test_svg_path_from_vertical_line_multi(self):
        self.assertPathParses('M3-2V5 6', {
            'first_point': ['3', '-2'],
            'width': 0,
            'height': 8,
            'num_segments': 1,
            })

    def test_svg_path_from_vertical_line_single_relative(self):
        self.assertPathParses('M3-2v5', {
            'first_point': ['3', '-2'],
            'width': 0,
            'height': 5,
            'num_segments': 1,
            })

    def test_svg_path_from_vertical_line_multi_relative(self):
        self.assertPathParses('M3-2v5 6', {
            'first_point': ['3', '-2'],
            'width': 0,
            'height': 11,
            'num_segments': 1,
            })

    def test_svg_path_from_horizontal_line_single(self):
        self.assertPathParses('M3-2H5', {
            'first_point': ['3', '-2'],
            'width': 2,
            'height': 0,
            'num_segments': 1,
            })

    def test_svg_path_from_horizontal_line_multi(self):
        self.assertPathParses('M3-2H5 6', {
            'first_point': ['3', '-2'],
            'width': 3,
            'height': 0,
            'num_segments': 1,
            })

    def test_svg_path_from_horizontal_line_single_relative(self):
        self.assertPathParses('M3-2h5', {
            'first_point': ['3', '-2'],
            'width': 5,
            'height': 0,
            'num_segments': 1,
            })

    def test_svg_path_from_horizontal_line_multi_relative(self):
        self.assertPathParses('M3-2h5 6', {
            'first_point': ['3', '-2'],
            'width': 11,
            'height': 0,
            'num_segments': 1,
            })

    def test_svg_path_from_line_single(self):
        self.assertPathParses('M3-2L7,1', {
            'first_point': ['3', '-2'],
            'width': 4,
            'height': 3,
            'num_segments': 1,
            })

    def test_svg_path_from_line_multi(self):
        self.assertPathParses('M3-2L7,1,7,-2', {
            'first_point': ['3', '-2'],
            'width': 4,
            'height': 3,
            'num_segments': 1,
            })

    def test_svg_path_from_line_single_relative(self):
        self.assertPathParses('M3-2l4,3', {
            'first_point': ['3', '-2'],
            'width': 4,
            'height': 3,
            'num_segments': 1,
            })

    def test_svg_path_from_line_multi_relative(self):
        self.assertPathParses('M3-2l4,3,0,-3', {
            'first_point': ['3', '-2'],
            'width': 4,
            'height': 3,
            'num_segments': 1,
            })

    @unittest.skip('arcs not implemented yet')
    def test_svg_path_from_arc_single(self):
        self.assertPathParses('M5,1A8,9 10 0 1 6,7', {
            'first_point': ['5', '1'],
            'num_segments': 1,
            })

    @unittest.skip('arcs not implemented yet')
    def test_svg_path_from_arc_multi(self):
        self.assertPathParses('M5,1A8,9 10 0 1 6,7 5,6 8 1 0 8,8', {
            'first_point': ['5', '1'],
            'num_segments': 1,
            })

    @unittest.skip('arcs not implemented yet')
    def test_svg_path_from_arc_single_relative(self):
        self.assertPathParses('M5,1a8,9 10 0 1 6,7', {
            'first_point': ['5', '1'],
            'num_segments': 1,
            })

    @unittest.skip('arcs not implemented yet')
    def test_svg_path_from_arc_multi_relative(self):
        self.assertPathParses('M5,1a8,9 10 0 1 6,7 5,6 8 1 0 8,8', {
            'first_point': ['5', '1'],
            'num_segments': 1,
            })

    def test_svg_path_from_quadratic_bezier_single(self):
        self.assertPathParses('M5,0Q10 5 15 0', {
            'first_point': ['5', '0'],
            'num_segments': 1,
            'width': 10,
            })

    def test_svg_path_from_quadratic_bezier_multi(self):
        self.assertPathParses('M5,0Q10 5 15 0 20 -5 25 0', {
            'first_point': ['5', '0'],
            'num_segments': 1,
            'width': 20,
            })

    def test_svg_path_from_quadratic_bezier_single_relative(self):
        self.assertPathParses('M5,0q5 5 10 0', {
            'first_point': ['5', '0'],
            'num_segments': 1,
            'width': 10,
            })

    def test_svg_path_from_quadratic_bezier_multi_relative(self):
        self.assertPathParses('M5,0q5 5 10 0 5 -5 10 0', {
            'first_point': ['5', '0'],
            'num_segments': 1,
            'width': 20,
            })

    @unittest.skip('smooth quadratic bezier dimensions calculation not implemented yet')
    def test_svg_path_from_smooth_quadratic_bezier_single(self):
        self.assertPathParses('M 3 4 T 5 6', {
            'first_point': ['3', '4'],
            'num_segments': 1,
            })

    @unittest.skip('smooth quadratic bezier dimensions calculation not implemented yet')
    def test_svg_path_from_smooth_quadratic_bezier_multi(self):
        self.assertPathParses('M 3 4 T 5 6 -1 -2', {
            'first_point': ['3', '4'],
            'num_segments': 1,
            })

    @unittest.skip('smooth quadratic bezier dimensions calculation not implemented yet')
    def test_svg_path_from_smooth_quadratic_bezier_single_relative(self):
        self.assertPathParses('M 3 4 t 5 6', {
            'first_point': ['3', '4'],
            'num_segments': 1,
            })

    @unittest.skip('smooth quadratic bezier dimensions calculation not implemented yet')
    def test_svg_path_from_smooth_quadratic_bezier_multi_relative(self):
        self.assertPathParses('M 3 4 t 5 6 -1 -2', {
            'first_point': ['3', '4'],
            'num_segments': 1,
            })

    def test_svg_from_curve_single(self):
        self.assertPathParses('M6-1C5,2 6,4 -5,-4', {
            'first_point': ['6', '-1'],
            'num_segments': 1,
            })

    def test_svg_from_curve_multi(self):
        self.assertPathParses('M6-1C5,2 6,4 -5,-4 1 2 3 4 5 6', {
            'first_point': ['6', '-1'],
            'num_segments': 1,
            })

    def test_svg_from_curve_single_relative(self):
        self.assertPathParses('M6-1c5,2 6,4 -5,-4', {
            'first_point': ['6', '-1'],
            'num_segments': 1,
            })

    def test_svg_from_curve_multi_relative(self):
        self.assertPathParses('M6-1c5,2 6,4 -5,-4 1 2 3 4 5 6', {
            'first_point': ['6', '-1'],
            'num_segments': 1,
            })

    @unittest.skip('smooth cubic bezier dimensions calculation not implemented yet')
    def test_svg_from_smooth_curve_single(self):
        self.assertPathParses('M6-1S5,2 6,4', {
            'first_point': ['6', '-1'],
            'num_segments': 1,
            })

    @unittest.skip('smooth cubic bezier dimensions calculation not implemented yet')
    def test_svg_from_smooth_curve_multi(self):
        self.assertPathParses('M6-1S5,2 6,4 1 2 3 4', {
            'first_point': ['6', '-1'],
            'num_segments': 1,
            })

    @unittest.skip('smooth cubic bezier dimensions calculation not implemented yet')
    def test_svg_from_smooth_curve_single_relative(self):
        self.assertPathParses('M6-1s5,2 6,4', {
            'first_point': ['6', '-1'],
            'num_segments': 1,
            })

    @unittest.skip('smooth cubic bezier dimensions calculation not implemented yet')
    def test_svg_from_smooth_curve_multi_relative(self):
        self.assertPathParses('M6-1s5,2 6,4 1 2 3 4', {
            'first_point': ['6', '-1'],
            'num_segments': 1,
            })

    def test_svg_path_close(self):
        self.assertPathParses('M5,8z', {
            'first_point': ['5', '8'],
            'width': 0,
            'height': 0,
            'num_segments': 1,
            })
