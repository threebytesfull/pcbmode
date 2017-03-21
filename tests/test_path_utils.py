try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pcbmode.utils.path_utils import *
from pcbmode.utils.point import Point

class TestPathUtils(unittest.TestCase):
    """Test path_utils functions"""

    # test boundary_box_check

    def test_boundary_box_with_single_point(self):
        p = Point()
        tl, br = boundary_box_check(p, p, p)
        self.assertEqual(tl, p)
        self.assertEqual(br, p)

    def test_boundary_box_with_contained_point(self):
        start_tl = Point(3,9)
        start_br = Point(8,5)
        p = Point(5,5)
        tl, br = boundary_box_check(start_tl, start_br, p)
        self.assertEqual(tl, start_tl)
        self.assertEqual(br, start_br)

    def test_boundary_box_with_uncontained_point_left(self):
        start_tl = Point(-3,6)
        start_br = Point(4,-5)
        p = Point(-5, 0)
        tl, br = boundary_box_check(start_tl, start_br, p)
        self.assertEqual(tl, Point(p.x, start_tl.y))
        self.assertEqual(br, start_br)

    def test_boundary_box_with_uncontained_point_right(self):
        start_tl = Point(-3,6)
        start_br = Point(4,-5)
        p = Point(5, 0)
        tl, br = boundary_box_check(start_tl, start_br, p)
        self.assertEqual(tl, start_tl)
        self.assertEqual(br, Point(p.x, start_br.y))

    def test_boundary_box_with_uncontained_point_top(self):
        start_tl = Point(-3,6)
        start_br = Point(4,-5)
        p = Point(0, 7)
        tl, br = boundary_box_check(start_tl, start_br, p)
        self.assertEqual(tl, Point(start_tl.x, p.y))
        self.assertEqual(br, start_br)

    def test_boundary_box_with_uncontained_point_bottom(self):
        start_tl = Point(-3,6)
        start_br = Point(4,-5)
        p = Point(0, -7)
        tl, br = boundary_box_check(start_tl, start_br, p)
        self.assertEqual(tl, start_tl)
        self.assertEqual(br, Point(start_br.x, p.y))

    def test_boundary_box_with_uncontained_point_top_left(self):
        start_tl = Point(-3,6)
        start_br = Point(4,-5)
        p = Point(-5, 7)
        tl, br = boundary_box_check(start_tl, start_br, p)
        self.assertEqual(tl, p)
        self.assertEqual(br, start_br)

    def test_boundary_box_with_uncontained_point_bottom_left(self):
        start_tl = Point(-3,6)
        start_br = Point(4,-5)
        p = Point(-5, -7)
        tl, br = boundary_box_check(start_tl, start_br, p)
        self.assertEqual(tl, Point(p.x, start_tl.y))
        self.assertEqual(br, Point(start_br.x, p.y))

    def test_boundary_box_with_uncontained_point_top_right(self):
        start_tl = Point(-3,6)
        start_br = Point(4,-5)
        p = Point(5, 7)
        tl, br = boundary_box_check(start_tl, start_br, p)
        self.assertEqual(tl, Point(start_tl.x, p.y))
        self.assertEqual(br, Point(p.x, start_br.y))

    def test_boundary_box_with_uncontained_point_bottom_right(self):
        start_tl = Point(-3,6)
        start_br = Point(4,-5)
        p = Point(5, -7)
        tl, br = boundary_box_check(start_tl, start_br, p)
        self.assertEqual(tl, start_tl)
        self.assertEqual(br, p)

    def test_boundary_box_with_point_on_border(self):
        start_tl = Point(-3,6)
        start_br = Point(4,-5)
        p = Point(-3,3)
        tl, br = boundary_box_check(start_tl, start_br, p)
        self.assertEqual(tl, start_tl)
        self.assertEqual(br, start_br)

    # test calculate_length_of_path_points

    @unittest.skip('number of points not yet checked')
    def test_length_of_zero_points(self):
        length = calculate_length_of_path_points([], [])
        self.assertEqual(length, 0, 'path with no points should return zero length')

    def test_length_of_one_point(self):
        points = ( (5,6), )
        length = calculate_length_of_path_points(*zip(*points))
        self.assertEqual(length, 0, 'path with one point should return zero length')

    def test_length_of_horizontal_path(self):
        points = ( (5,3), (6,3), (7,3) )
        length = calculate_length_of_path_points(*zip(*points))
        self.assertEqual(length, 2, 'length of horizontal path should be calculated correctly')

    def test_length_of_vertical_path(self):
        points = ( (-3,7), (-3,0), (-3,-7) )
        length = calculate_length_of_path_points(*zip(*points))
        self.assertEqual(length, 14, 'length of vertical path should be calculated correctly')

    def test_length_of_diagonal_path(self):
        points = ( (0,0), (3,4) )
        length = calculate_length_of_path_points(*zip(*points))
        self.assertEqual(length, 5, 'length of diagonal path should be calculated correctly')

    def test_length_of_complex_path(self):
        points = ( (0,0), (3,4), (5,4), (8,0), (8,-1), (0,-1), (0,0) )
        length = calculate_length_of_path_points(*zip(*points))
        self.assertEqual(length, 22, 'length of complex path should be calculated correctly')

    # test calculate_points_of_quadratic_bezier

    def test_calculate_points_of_quadratic_bezier(self):
        """Check forward differencing calculation of quadratic bezier against simple long calculation"""
        test_curves = (
            ( (0,0), (5,5), (10,0) ),
            ( (50,0), (80,50), (100,0) ),
            ( (-3,6), (7,9), (12,7) ),
        )

        def quadratic_bezier_point(p0, p1, p2, t):
            t2 = t*t
            mt = 1.0-t
            mt2 = mt*mt
            return p0*mt2 + p1*2*mt*t + p2*t2

        for curve in test_curves:
            with self.subTest(curve=curve):
                x_coords_in, y_coords_in = zip(*curve)
                for steps in (10, 100):
                    with self.subTest(steps=steps):
                        x_coords_out = calculate_points_of_quadratic_bezier(x_coords_in, steps=steps)
                        y_coords_out = calculate_points_of_quadratic_bezier(y_coords_in, steps=steps)
                        self.assertEqual(len(x_coords_out), steps+1) # TODO: should this really be +1?
                        self.assertEqual(len(y_coords_out), steps+1) # TODO: should this really be +1?
                        # check points against quadratic bezier formula
                        delta_t = 1.0/steps
                        for step in range(steps):
                            t = delta_t*step
                            calc_x = quadratic_bezier_point(*(x_coords_in + (t,)))
                            calc_y = quadratic_bezier_point(*(y_coords_in + (t,)))
                            self.assertAlmostEqual(x_coords_out[step], calc_x, delta=1e-12)
                            self.assertAlmostEqual(y_coords_out[step], calc_y, delta=1e-12)

    # test calculate_points_of_cubic_bezier

    def test_calculate_points_of_cubic_bezier(self):
        """Check forward differencing calculation of cubic bezier against simple long calculation"""
        test_curves = (
            ( (0,0), (0,5), (10,5), (10,0) ),
            ( (50,0), (80,50), (80,50), (100,0) ),
            ( (-3,6), (7,9), (1.5,4), (12,7) ),
        )

        def cubic_bezier_point(p0, p1, p2, p3, t):
            t2 = t*t
            t3 = t2*t
            mt = 1.0-t
            mt2 = mt*mt
            mt3 = mt2*mt
            return p0*mt3 + p1*3*mt2*t + p2*3*mt*t2 + p3*t3

        for curve in test_curves:
            with self.subTest(curve=curve):
                x_coords_in, y_coords_in = zip(*curve)
                for steps in (10, 100):
                    with self.subTest(steps=steps):
                        x_coords_out = calculate_points_of_cubic_bezier(x_coords_in, steps=steps)
                        y_coords_out = calculate_points_of_cubic_bezier(y_coords_in, steps=steps)
                        self.assertEqual(len(x_coords_out), steps+1) # TODO: should this really be +1?
                        self.assertEqual(len(y_coords_out), steps+1) # TODO: should this really be +1?
                        # check points against cubic bezier formula
                        delta_t = 1.0/steps
                        for step in range(steps):
                            t = delta_t*step
                            calc_x = cubic_bezier_point(*(x_coords_in + (t,)))
                            calc_y = cubic_bezier_point(*(y_coords_in + (t,)))
                            self.assertAlmostEqual(x_coords_out[step], calc_x, delta=1e-12)
                            self.assertAlmostEqual(y_coords_out[step], calc_y, delta=1e-12)
