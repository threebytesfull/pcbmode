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
from pcbmode.utils.point import Point
from pcbmode.utils.svgpath import SvgPath
from pcbmode.utils.svg_grammar import SvgGrammar

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

    def test_would_notify_unhandled_but_parsed_command_in_make_relative(self):
        """If the parser matched an element not handled in the if statements, it should be notified at the bottom"""
        # fake a property because patch doesn't see the inner class being returned
        # TODO: find a better way to do this without needing SvgGrammar here...
        SvgGrammar.grammar = None
        with patch('pcbmode.utils.svg_grammar.SvgGrammar.grammar') as grammar_method:
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
        if 'top_left' in expected_results:
            self.assertEqual(path.top_left, expected_results['top_left'], 'should get correct bounding box top left corner')
        if 'bottom_right' in expected_results:
            self.assertEqual(path.bottom_right, expected_results['bottom_right'], 'should get correct bounding box bottom right corner')
        return path

    def test_svg_paths_share_grammar_instance(self):
        path = SvgPath('M 1 2')
        self.assertTrue(hasattr(path, 'grammar'), 'path should have a grammar property')
        path2 = SvgPath('M 3 4')
        self.assertIs(path2.grammar, path.grammar, 'paths should share grammar instance')

    def test_svg_path_from_same_svg_string(self):
        svg_string = 'M 9 8'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        path2 = SvgPath(svg_string)
        self.assertIs(path.getFirstPoint(), path2.getFirstPoint(), 'should get same path as first point object')

    def test_svg_path_from_move_single(self):
        self.assertPathParses('M 1 2', {
            'first_point': ['1', '2'],
            'width': 0,
            'height': 0,
            'num_segments': 1,
            'top_left': Point(1,2),
            'bottom_right': Point(1,2),
            })

    def test_svg_path_from_move_single_relative(self):
        self.assertPathParses('m 1 2', {
            'first_point': ['1', '2'],
            'width': 0,
            'height': 0,
            'num_segments': 1,
            'top_left': Point(1,2),
            'bottom_right': Point(1,2),
            })

    def test_svg_path_from_move_multi(self):
        self.assertPathParses('M 1 2 3 4', {
            'first_point': ['1', '2'],
            'width': 2,
            'height': 2,
            'num_segments': 1,
            'top_left': Point(1,4),
            'bottom_right': Point(3,2),
            })

    def test_svg_path_from_move_multi_relative(self):
        self.assertPathParses('m 1 2 3 4', {
            'first_point': ['1', '2'],
            'width': 3,
            'height': 4,
            'num_segments': 1,
            'top_left': Point(1,6),
            'bottom_right': Point(4,2),
            })

    def test_svg_path_from_moves_single(self):
        self.assertPathParses('M 1 2 M 3 4', {
            'first_point': ['1', '2'],
            'width': 2,
            'height': 2,
            'num_segments': 2,
            'top_left': Point(1,4),
            'bottom_right': Point(3,2),
            })
        # first move being relative should make no difference
        self.assertPathParses('m 1 2 M 3 4', {
            'first_point': ['1', '2'],
            'width': 2,
            'height': 2,
            'num_segments': 2,
            'top_left': Point(1,4),
            'bottom_right': Point(3,2),
            })

    def test_svg_path_from_moves_single_relative(self):
        self.assertPathParses('M 1 2 m 3 4', {
            'first_point': ['1', '2'],
            'width': 3,
            'height': 4,
            'num_segments': 2,
            'top_left': Point(1,6),
            'bottom_right': Point(4,2),
            })

    def test_svg_path_from_vertical_line_single(self):
        self.assertPathParses('M3-2V5', {
            'first_point': ['3', '-2'],
            'width': 0,
            'height': 7,
            'num_segments': 1,
            'top_left': Point(3,5),
            'bottom_right': Point(3,-2),
            })

    def test_svg_path_from_vertical_line_multi(self):
        self.assertPathParses('M3-2V5 6', {
            'first_point': ['3', '-2'],
            'width': 0,
            'height': 8,
            'num_segments': 1,
            'top_left': Point(3,6),
            'bottom_right': Point(3,-2),
            })

    def test_svg_path_from_vertical_line_single_relative(self):
        self.assertPathParses('M3-2v5', {
            'first_point': ['3', '-2'],
            'width': 0,
            'height': 5,
            'num_segments': 1,
            'top_left': Point(3,3),
            'bottom_right': Point(3,-2),
            })

    def test_svg_path_from_vertical_line_multi_relative(self):
        self.assertPathParses('M3-2v5 6', {
            'first_point': ['3', '-2'],
            'width': 0,
            'height': 11,
            'num_segments': 1,
            'top_left': Point(3,9),
            'bottom_right': Point(3,-2),
            })

    def test_svg_path_from_horizontal_line_single(self):
        self.assertPathParses('M3-2H5', {
            'first_point': ['3', '-2'],
            'width': 2,
            'height': 0,
            'num_segments': 1,
            'top_left': Point(3,-2),
            'bottom_right': Point(5,-2),
            })

    def test_svg_path_from_horizontal_line_multi(self):
        self.assertPathParses('M3-2H5 6', {
            'first_point': ['3', '-2'],
            'width': 3,
            'height': 0,
            'num_segments': 1,
            'top_left': Point(3,-2),
            'bottom_right': Point(6,-2),
            })

    def test_svg_path_from_horizontal_line_single_relative(self):
        self.assertPathParses('M3-2h5', {
            'first_point': ['3', '-2'],
            'width': 5,
            'height': 0,
            'num_segments': 1,
            'top_left': Point(3,-2),
            'bottom_right': Point(8,-2),
            })

    def test_svg_path_from_horizontal_line_multi_relative(self):
        self.assertPathParses('M3-2h5 6', {
            'first_point': ['3', '-2'],
            'width': 11,
            'height': 0,
            'num_segments': 1,
            'top_left': Point(3,-2),
            'bottom_right': Point(14,-2),
            })

    def test_svg_path_from_line_single(self):
        self.assertPathParses('M3-2L7,1', {
            'first_point': ['3', '-2'],
            'width': 4,
            'height': 3,
            'num_segments': 1,
            'top_left': Point(3,1),
            'bottom_right': Point(7,-2),
            })

    def test_svg_path_from_line_multi(self):
        self.assertPathParses('M3-2L7,1,7,-2', {
            'first_point': ['3', '-2'],
            'width': 4,
            'height': 3,
            'num_segments': 1,
            'top_left': Point(3,1),
            'bottom_right': Point(7,-2),
            })

    def test_svg_path_from_line_single_relative(self):
        self.assertPathParses('M3-2l4,3', {
            'first_point': ['3', '-2'],
            'width': 4,
            'height': 3,
            'num_segments': 1,
            'top_left': Point(3,1),
            'bottom_right': Point(7,-2),
            })

    def test_svg_path_from_line_multi_relative(self):
        self.assertPathParses('M3-2l4,3,0,-3', {
            'first_point': ['3', '-2'],
            'width': 4,
            'height': 3,
            'num_segments': 1,
            'top_left': Point(3,1),
            'bottom_right': Point(7,-2),
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
            'top_left': Point(5,2.5),
            'bottom_right': Point(15,0),
            })

    def test_svg_path_from_quadratic_bezier_multi(self):
        self.assertPathParses('M5,0Q10 5 15 0 20 -5 25 0', {
            'first_point': ['5', '0'],
            'num_segments': 1,
            'width': 20,
            'top_left': Point(5,2.5),
            'bottom_right': Point(25,-2.5),
            })

    def test_svg_path_from_quadratic_bezier_single_relative(self):
        self.assertPathParses('M5,0q5 5 10 0', {
            'first_point': ['5', '0'],
            'num_segments': 1,
            'width': 10,
            'top_left': Point(5,2.5),
            'bottom_right': Point(15,0),
            })

    def test_svg_path_from_quadratic_bezier_multi_relative(self):
        self.assertPathParses('M5,0q5 5 10 0 5 -5 10 0', {
            'first_point': ['5', '0'],
            'num_segments': 1,
            'width': 20,
            'top_left': Point(5,2.5),
            'bottom_right': Point(25,-2.5),
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

    def test_get_relative(self):
        test_cases = {
            # moveto
            'M5,8 6,8 2-2z': 'm 5.0,8.0 1.0,0.0 -4.0,-10.0 z ',
            'm5,8 6,8 2-2z': 'm 5.0,8.0 6.0,8.0 2.0,-2.0 z ',
            # horizontal lineto
            'M3,4 H 5': 'm 3.0,4.0 h 2.0 ',
            'M3,4 H 5-3': 'm 3.0,4.0 h 2.0 -8.0 ',
            'M3,4 h 5': 'm 3.0,4.0 h 5.0 ',
            'M3,4 h 5-3': 'm 3.0,4.0 h 5.0 -3.0 ',
            # vertical lineton
            'M-3,4V2': 'm -3.0,4.0 v -2.0 ',
            'M-3,4V2-5': 'm -3.0,4.0 v -2.0 -7.0 ',
            'M5,6v-2.4': 'm 5.0,6.0 v -2.4 ',
            'M5,6v-2.4-5': 'm 5.0,6.0 v -2.4 -5.0 ',
            # lineto
            'M42,1L15,3-1-1': 'm 42.0,1.0 l -27.0,2.0 -16.0,-4.0 ',
            'M42,1l15,3-1-1': 'm 42.0,1.0 l 15.0,3.0 -1.0,-1.0 ',
            # cubic curveto
            'M4,3C5,5,7,5,9,3': 'm 4.0,3.0 c 1.0,2.0 3.0,2.0 5.0,0.0 ',
            'M4,3C5,5,7,5,9,3 7,6 5,4 3,2': 'm 4.0,3.0 c 1.0,2.0 3.0,2.0 5.0,0.0 -2.0,3.0 -4.0,1.0 -6.0,-1.0 ',
            'M4,3c5,5,7,5,9,3': 'm 4.0,3.0 c 5.0,5.0 7.0,5.0 9.0,3.0 ',
            'M4,3c5,5,7,5,9,3 7,6 5,4 3,2': 'm 4.0,3.0 c 5.0,5.0 7.0,5.0 9.0,3.0 7.0,6.0 5.0,4.0 3.0,2.0 ',
            # smooth cubic curveto
            'M4,3S5,5 7,3': 'm 4.0,3.0 s 1.0,2.0 3.0,0.0 ',
            'M4,3S5,5 7,3 8,5 4,2': 'm 4.0,3.0 s 1.0,2.0 3.0,0.0 1.0,2.0 -3.0,-1.0 ',
            'M4,3s5,5 7,3': 'm 4.0,3.0 s 5.0,5.0 7.0,3.0 ',
            # quadratic curveto
            'M42,1Q40,0 45,5': 'm 42.0,1.0 q -2.0,-1.0 3.0,4.0 ',
            'M42,1Q40,0 45,5 47.5,-2 50,5': 'm 42.0,1.0 q -2.0,-1.0 3.0,4.0 2.5,-7.0 5.0,0.0 ',
            'M42,1q40,0 45,5': 'm 42.0,1.0 q 40.0,0.0 45.0,5.0 ',
            'M42,1q40,0 45,5 47.5,-2 50,5': 'm 42.0,1.0 q 40.0,0.0 45.0,5.0 47.5,-2.0 50.0,5.0 ',
            # smooth quadratic curveto
            'M9,8T7,6': 'm 9.0,8.0 t -2.0,-2.0 ',
            'M9,8T7,6 5,4': 'm 9.0,8.0 t -2.0,-2.0 -2.0,-2.0 ',
            'M9,8t7,6': 'm 9.0,8.0 t 7.0,6.0 ',
            'M9,8t7,6 5,4': 'm 9.0,8.0 t 7.0,6.0 5.0,4.0 ',
            # closepath
            'M42,1Z': 'm 42.0,1.0 z ',
            'M-3,2z': 'm -3.0,2.0 z ',
        }
        for test_input, expected_output in test_cases.items():
            with self.subTest(svg=test_input):
                path = SvgPath(test_input)
                self.assertEqual(path.getRelative(), expected_output)

    def test_get_relative_parsed(self):
        test_cases = {
            # moveto
            'M5,8 6,8 2-2z': [['m', ['5.0', '8.0'], ['1.0', '0.0'], ['-4.0', '-10.0']], ['z']],
            'm5,8 6,8 2-2z': [['m', ['5.0', '8.0'], ['6.0', '8.0'], ['2.0', '-2.0']], ['z']],
            # horizontal lineto
            'M3,4 H 5': [['m', ['3.0', '4.0']], ['h', ['2.0']]],
            'M3,4 H 5-3': [['m', ['3.0', '4.0']], ['h', ['2.0'], ['-8.0']]],
            'M3,4 h 5': [['m', ['3.0', '4.0']], ['h', ['5.0']]],
            'M3,4 h 5-3': [['m', ['3.0', '4.0']], ['h', ['5.0'], ['-3.0']]],
            # vertical lineton
            'M-3,4V2': [['m', ['-3.0', '4.0']], ['v', ['-2.0']]],
            'M-3,4V2-5': [['m', ['-3.0', '4.0']], ['v', ['-2.0'], ['-7.0']]],
            'M5,6v-2.4': [['m', ['5.0', '6.0']], ['v', ['-2.4']]],
            'M5,6v-2.4-5': [['m', ['5.0', '6.0']], ['v', ['-2.4'], ['-5.0']]],
            # lineto
            'M42,1L15,3-1-1': [['m', ['42.0', '1.0']], ['l', ['-27.0', '2.0'], ['-16.0', '-4.0']]],
            'M42,1l15,3-1-1': [['m', ['42.0', '1.0']], ['l', ['15.0', '3.0'], ['-1.0', '-1.0']]],
            # cubic curveto
            'M4,3C5,5,7,5,9,3': [['m', ['4.0', '3.0']], ['c', ['1.0', '2.0'], ['3.0', '2.0'], ['5.0', '0.0']]],
            'M4,3C5,5,7,5,9,3 7,6 5,4 3,2': [['m', ['4.0', '3.0']], ['c', ['1.0', '2.0'], ['3.0', '2.0'], ['5.0', '0.0'], ['-2.0', '3.0'], ['-4.0', '1.0'], ['-6.0', '-1.0']]],
            'M4,3c5,5,7,5,9,3': [['m', ['4.0', '3.0']], ['c', ['5.0', '5.0'], ['7.0', '5.0'], ['9.0', '3.0']]],
            'M4,3c5,5,7,5,9,3 7,6 5,4 3,2': [['m', ['4.0', '3.0']], ['c', ['5.0', '5.0'], ['7.0', '5.0'], ['9.0', '3.0'], ['7.0', '6.0'], ['5.0', '4.0'], ['3.0', '2.0']]],
            # smooth cubic curveto
            'M4,3S5,5 7,3': [['m', ['4.0', '3.0']], ['s', ['1.0', '2.0'], ['3.0', '0.0']]],
            'M4,3S5,5 7,3 8,5 4,2': [['m', ['4.0', '3.0']], ['s', ['1.0', '2.0'], ['3.0', '0.0'], ['1.0', '2.0'], ['-3.0', '-1.0']]],
            'M4,3s5,5 7,3': [['m', ['4.0', '3.0']], ['s', ['5.0', '5.0'], ['7.0', '3.0']]],
            # quadratic curveto
            'M42,1Q40,0 45,5': [['m', ['42.0', '1.0']], ['q', ['-2.0', '-1.0'], ['3.0', '4.0']]],
            'M42,1Q40,0 45,5 47.5,-2 50,5': [['m', ['42.0', '1.0']], ['q', ['-2.0', '-1.0'], ['3.0', '4.0'], ['2.5', '-7.0'], ['5.0', '0.0']]],
            'M42,1q40,0 45,5': [['m', ['42.0', '1.0']], ['q', ['40.0', '0.0'], ['45.0', '5.0']]],
            'M42,1q40,0 45,5 47.5,-2 50,5': [['m', ['42.0', '1.0']], ['q', ['40.0', '0.0'], ['45.0', '5.0'], ['47.5', '-2.0'], ['50.0', '5.0']]],
            # smooth quadratic curveto
            'M9,8T7,6': [['m', ['9.0', '8.0']], ['t', ['-2.0', '-2.0']]],
            'M9,8T7,6 5,4': [['m', ['9.0', '8.0']], ['t', ['-2.0', '-2.0'], ['-2.0', '-2.0']]],
            'M9,8t7,6': [['m', ['9.0', '8.0']], ['t', ['7.0', '6.0']]],
            'M9,8t7,6 5,4': [['m', ['9.0', '8.0']], ['t', ['7.0', '6.0'], ['5.0', '4.0']]],
            # closepath
            'M42,1Z': [['m', ['42.0', '1.0']], ['z']],
            'M-3,2z': [['m', ['-3.0', '2.0']], ['z']],
        }
        for test_input, expected_output in test_cases.items():
            with self.subTest(svg=test_input):
                path = SvgPath(test_input)
                self.assertEqual(path.getRelativeParsed(), expected_output)

    def test_transform_with_defaults(self):
        path = SvgPath('M1 2')
        path.transform()
        self.assertEqual(path.getFirstPoint(), ['1','2'], 'transform should make no changes by default')

    def test_transform_uses_cache(self):
        svg_string = 'M1 2 H 5'

        path1 = SvgPath(svg_string)
        path1.transform(scale=3)
        t1 = path1.getTransformed()

        path2 = SvgPath(svg_string)
        path2.transform(scale=3)
        t2 = path2.getTransformed()

        self.assertIs(t1, t2, 'same transformation on same path should hit cache')

    def test_transform_with_scale(self):
        path = SvgPath('M1 2 3 4')
        self.assertEqual(path.top_left, Point(1,4))
        self.assertEqual(path.bottom_right, Point(3,2))
        self.assertEqual(path.getWidth(), 2)
        self.assertEqual(path.getHeight(), 2)

        # path should be centred and then scaled around origin
        path.transform(scale=2)
        self.assertEqual(path.getWidth(), 4)
        self.assertEqual(path.getHeight(), 4)
        self.assertEqual(path.top_left, Point(-2,2))
        self.assertEqual(path.bottom_right, Point(2,-2))
        # TODO: sort out rounding issue with transformed path?
        #self.assertEqual(path.getTransformed(), 'm -2.0,-2.0 4.0,4.0 ')
        #self.assertEqual(path.getTransformedMirrored(), 'm 2.0,-2.0 -4.0,4.0 ')
        # TODO: first point should get updated!
        #self.assertEqual(path.getFirstPoint(), ['-2','-2'])

    def test_transform_with_scale_uncentred(self):
        path = SvgPath('M1 2 3 4')
        self.assertEqual(path.top_left, Point(1,4))
        self.assertEqual(path.bottom_right, Point(3,2))
        self.assertEqual(path.getWidth(), 2)
        self.assertEqual(path.getHeight(), 2)

        # path should be scaled around its own centre
        path.transform(scale=2, center=False)
        self.assertEqual(path.top_left, Point(2,8))
        self.assertEqual(path.bottom_right, Point(6,4))
        self.assertEqual(path.getWidth(), 4)
        self.assertEqual(path.getHeight(), 4)
        # TODO: sort out rounding issue with transformed path?
        #self.assertEqual(path.getTransformed(), 'm 2.0,4.0 4.0,4.0 ')
        #self.assertEqual(path.getTransformedMirrored(), 'm 4.0,4.0 -4.0,4.0 ')
        # TODO: first point should get updated!
        #self.assertEqual(path.getFirstPoint(), ['2','4'])

    def test_transform_with_mirror(self):
        path = SvgPath('M1 2 3 4')
        self.assertEqual(path.top_left, Point(1,4))
        self.assertEqual(path.bottom_right, Point(3,2))
        self.assertEqual(path.getWidth(), 2)
        self.assertEqual(path.getHeight(), 2)
        self.assertEqual(path.getRelative(), 'm 1.0,2.0 2.0,2.0 ')

        # path should be centred and then mirrored around origin
        path.transform(mirror=True)
        self.assertEqual(path.top_left, Point(-1,1))
        self.assertEqual(path.bottom_right, Point(1,-1))
        self.assertEqual(path.getWidth(), 2)
        self.assertEqual(path.getHeight(), 2)
        self.assertEqual(path.getRelative(), 'm 1.0,2.0 2.0,2.0 ')
        # TODO: sort out rounding issue with transformed path?
        #self.assertEqual(path.getTransformed(), 'm 1.0,-1.0 -2.0,2.0 ')
        # TODO: first point should get updated!
        #self.assertEqual(path.getFirstPoint(), ['-2','-2'])

    def test_transform_with_mirror_uncentred(self):
        path = SvgPath('M1 2 3 4')
        self.assertEqual(path.top_left, Point(1,4))
        self.assertEqual(path.bottom_right, Point(3,2))
        self.assertEqual(path.getWidth(), 2)
        self.assertEqual(path.getHeight(), 2)
        self.assertEqual(path.getRelative(), 'm 1.0,2.0 2.0,2.0 ')

        # path should be mirrored around its own centre
        path.transform(mirror=True, center=False)
        self.assertEqual(path.top_left, Point(1,4))
        self.assertEqual(path.bottom_right, Point(3,2))
        self.assertEqual(path.getWidth(), 2)
        self.assertEqual(path.getHeight(), 2)
        self.assertEqual(path.getRelative(), 'm 1.0,2.0 2.0,2.0 ')
        # TODO: sort out rounding issue with transformed path?
        #self.assertEqual(path.getTransformed(), 'm 1.0,-1.0 -2.0,2.0 ')
        # TODO: first point should get updated!
        #self.assertEqual(path.getFirstPoint(), ['-2','-2'])
