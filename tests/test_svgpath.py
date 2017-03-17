import unittest
from unittest.mock import patch

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

    def test_svg_path_from_move_single(self):
        svg_string = 'M 1 2'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['1','2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 0, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 0, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_same_svg_string(self):
        svg_string = 'M 9 8'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        path2 = SvgPath(svg_string)
        self.assertIs(path.getFirstPoint(), path2.getFirstPoint(), 'should get same path first point object')

    def test_svg_path_from_move_single_relative(self):
        svg_string = 'm1 2'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['1','2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 0, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 0, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_move_multi(self):
        svg_string = 'M 1 2 3 4'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['1','2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 2, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 2, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_move_multi_relative(self):
        svg_string = 'm 1 2 3 4'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['1','2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 3, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 4, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_moves_single(self):
        svg_string = 'M 1 2 M 3 4'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['1','2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 2, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 2, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 2, 'should get correct number of segments')
        # first move being relative should make no difference
        svg_string = 'm 1 2 M 3 4'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['1','2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 2, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 2, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 2, 'should get correct number of segments')

    def test_svg_path_from_moves_single_relative(self):
        svg_string = 'M 1 2 m 3 4'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['1','2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 3, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 4, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 2, 'should get correct number of segments')

    def test_svg_path_from_vertical_line_single(self):
        svg_string = 'M 3 -2 V 5'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 0, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 7, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_vertical_line_multi(self):
        svg_string = 'M 3 -2 V 5 6'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 0, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 8, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_vertical_line_single_relative(self):
        svg_string = 'M 3 -2 v 5'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 0, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 5, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_vertical_line_multi_relative(self):
        svg_string = 'M 3 -2 v 5 6'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 0, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 11, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_horizontal_line_single(self):
        svg_string = 'M 3 -2 H 5'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 2, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 0, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_horizontal_line_multi(self):
        svg_string = 'M 3 -2 H 5 6'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 3, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 0, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_horizontal_line_single_relative(self):
        svg_string = 'M 3 -2 h 5'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 5, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 0, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_horizontal_line_multi_relative(self):
        svg_string = 'M 3 -2 h 5 6'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 11, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 0, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_line_single(self):
        svg_string = 'M 3 -2 L 7 1'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 4, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 3, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_line_multi(self):
        svg_string = 'M 3 -2 L 7 1 7 -2'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 4, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 3, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_line_single_relative(self):
        svg_string = 'M 3 -2 l 4 3'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 4, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 3, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_from_line_multi_relative(self):
        svg_string = 'M 3 -2 l 4 3 0 -3'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['3', '-2'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 4, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 3, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')

    def test_svg_path_close(self):
        svg_string = 'M 5 8 z'
        path = SvgPath(svg_string)
        self.assertEqual(path.getOriginal(), svg_string, 'getOriginal should return original SVG path')
        self.assertEqual(path.getFirstPoint(), ['5', '8'], 'getFirstPoint should return first move point')
        self.assertEqual(path.getWidth(), 0, 'should calculate correct width')
        self.assertEqual(path.getHeight(), 0, 'should calculate correct height')
        self.assertEqual(path.getNumberOfSegments(), 1, 'should get correct number of segments')
