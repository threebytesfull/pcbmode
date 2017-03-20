try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pcbmode.utils.svg import *


class TestPcbmode(unittest.TestCase):
    """Test pcbmode script"""

    def test_absolute_to_relative_path(self):
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

    def test_coord_list_to_svg_path(self):
        pass
