import unittest
from unittest.mock import patch

from pcbmode.utils.svg import *


class TestPcbmode(unittest.TestCase):
    """Test pcbmode script"""

    # svg_grammar tests
    def test_svg_grammar(self):
        grammar = svg_grammar()
        self.assertIsNotNone(grammar, 'should compile SVG grammar')

        svg_good_examples = [
            # M=moveto absolute
            'M 15, -3',
            'M-3,2.0',
            'M 1.2, 3.5',
            'M 3,4 6,5 8 9 10 11',
            # m=moveto relative
            'm 3,0',
            'm1,1',
            ' m 7 8',
            'm -1 -2 -3 -4 5 6 7.8 9',
            # C=curveto absolute (cubic bezier)
            'C1,2,3,4,5,6',
            'C 1,2 3,4 5,6',
            'C -1,3.2 5.6,7 8,0.9',
            # c=curveto relative (cubic bezier)
            'c1,2,3,4,5,6',
            'c 1,2 3,4 5,6',
            ' c -1,3.2 5.6,7 8,0.9',
            # Q=curveto absolute (quadratic bezier)
            'Q1,2,3,4',
            'Q 1,2 3,4',
            'Q -1,3.2 5.6,7',
            # q=curveto relative (quadratic bezier)
            'q1,2,3,4',
            'q 1,2 3,4',
            ' q -1,3.2 5.6,7',
            # T=smooth curveto absolute (quadratic bezier)
            'T 15, -3',
            'T-3,2.0',
            'T 1.2, 3.5',
            # t=smooth curveto relative (quadratic bezier)
            't 3,0',
            't1,1',
            ' t 7 8',
            # S=smooth curveto absolute
            'S1,2,3,4',
            'S 1,2 3,4',
            'S -1,3.2 5.6,7',
            # s=smooth curveto relative
            's1,2,3,4',
            's 1,2 3,4',
            ' s -1,3.2 5.6,7',
            # L=lineto absolute
            'L 15, -3',
            'L-3,2.0',
            'L 1.2, 3.5',
            # l=lineto relative
            'l 3,0',
            'l1,1',
            ' l 7 8',
            # H=horizontal lineto absolute
            'H 15',
            'H-3.2',
            'H 1.2',
            # h=horizontal lineto relative
            'h 3',
            'h1.1',
            ' h 7',
            # V=vertical lineto absolute
            'V 15',
            'V-3.2',
            'V 1.2',
            # v=vertical lineto relative
            'v 3',
            'v1.1',
            ' v 7',
            # A=arcto absolute
            #'A20,20 0 0,0 40,40',
            # a=arcto relative
            # z=closepath
            'z',
            'Z',
            'z ',
            # combined
            'M10,10 L20,5 v-10 h-25 z',
            'M10,10L20,5v-10h-25z',
            'M8-29q17-29 12 29q-7 29-23-11t11-17z',
        ]

        for path in svg_good_examples:
            with self.subTest(path=path):
                parse_result = grammar.parseString(path)

    def test_absolute_to_relative_path(self):
        pass

    def test_relative_svg_path_to_absolute_coord_list(self):
        pass

    def test_mirror_path_over_axis(self):
        pass

    def test_boundary_box_check(self):
        pass

    def test_calculate_bounding_box_of_path(self):
        pass

    def test_calculate_points_of_cubic_bezier(self):
        pass

    def test_transform_path(self):
        pass

    def test_get_width_and_height_of_shape_from_two_points(self):
        pass

    def test_width_and_height_to_path(self):
        pass

    def test_ring_diameters_to_path(self):
        pass

    def test_circle_diameter_to_path(self):
        pass

    def test_drillPath(self):
        pass

    def test_placementMarkerPath(self):
        pass

    def test_mirror_transform(self):
        pass

    def test_makeSvgLayers(self):
        pass

    def test_makeSvgLayer(self):
        pass

    def test_create_layers_for_gerber_svg(self):
        pass

    def test_rect_to_path(self):
        pass

    def test_create_meandering_path(self):
        pass

    def test_create_round_meander(self):
        pass

    def test_calculate_cubic_bezier_length(self):
        pass

    def test_coord_list_to_svg_path(self):
        pass
