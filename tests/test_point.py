import unittest

from pcbmode.utils.point import Point

class TestPoint(unittest.TestCase):
    """Test Point class"""

    def setUp(self):
        self.p0 = Point(3, 4)
        self.p1 = Point(4/3, 5.001)
        self.p2 = Point(-1/12, 0)

    # Tests for __init__
    def test_point_with_no_coordinates(self):
        p = Point()
        self.assertIsInstance(p, Point, 'should create a Point')
        self.assertEqual(p.x, 0, 'default x should be 0')
        self.assertEqual(p.y, 0, 'default y should be 0')

    def test_point_positional_x_and_y(self):
        p = Point(3, 4)
        self.assertIsInstance(p, Point, 'should create a Point with x and y coords')
        self.assertEqual(p.x, 3, 'should store x coordinate')
        self.assertEqual(p.y, 4, 'should store y coordinate')

    def test_point_with_positional_x_only(self):
        p = Point(3)
        self.assertIsInstance(p, Point, 'should create a Point with positional x coord only')
        self.assertEqual(p.x, 3, 'should store x coordinate')
        self.assertEqual(p.y, 0, 'should use default y coordinate')

    def test_point_with_named_x_only(self):
        p = Point(x=3)
        self.assertIsInstance(p, Point, 'should create a Point with named x coord only')
        self.assertEqual(p.x, 3, 'should store x coordinate')
        self.assertEqual(p.y, 0, 'should use default y coordinate')

    def test_point_with_named_y_only(self):
        p = Point(y=4)
        self.assertIsInstance(p, Point, 'should create a Point with named y coord only')
        self.assertEqual(p.x, 0, 'should use default x coordinate')
        self.assertEqual(p.y, 4, 'should store y coordinate')

    # Tests for __add__
    def test_add_points(self):
        p3 = self.p1 + self.p2
        self.assertEqual(p3.x, self.p1.x + self.p2.x, 'should add x coords correctly')
        self.assertEqual(p3.y, self.p1.y + self.p2.y, 'should add y coords correctly')

    # Tests for __sub__
    def test_sub_points(self):
        p3 = self.p1 - self.p2
        self.assertEqual(p3.x, self.p1.x - self.p2.x, 'should sub x coords correctly')
        self.assertEqual(p3.y, self.p1.y - self.p2.y, 'should sub y coords correctly')

    # Tests for __repr__
    def test_string_representation(self):
        self.assertEqual(repr(self.p0), '[3.00, 4.00]', 'should get representation rounded to two decimal places')
        self.assertEqual(repr(self.p1), '[1.33, 5.00]', 'should get representation rounded to two decimal places')
        self.assertEqual(repr(self.p2), '[-0.08, 0.00]', 'should get representation rounded to two decimal places')

    # Tests for __eq__
    def test_equality(self):
        self.assertTrue(self.p0 == self.p0, 'point should equal itself')
        self.assertTrue(self.p0 == Point(self.p0.x, self.p0.y), 'point should equal a similar point')
        self.assertFalse(self.p0 == self.p1, 'point should not equal a different point')

    # Tests for __ne__
    def test_inequality(self):
        self.assertFalse(self.p0 != self.p0, 'point should equal itself')
        self.assertFalse(self.p0 != Point(self.p0.x, self.p0.y), 'point should equal a similar point')
        self.assertTrue(self.p0 != self.p1, 'point should not equal a different point')

    # Tests for assign
    def test_assignment(self):
        new_point = Point(5, 6)
        self.assertNotEqual(self.p0, new_point, 'points should not be equal before assignment')
        self.p0.assign(5, 6)
        self.assertEqual(self.p0, new_point, 'points should be equal after assigment with positional x and y')

        self.assertNotEqual(self.p1.x, new_point.x, 'x coords should not be equal before assignment')
        self.p1.assign(x=new_point.x)
        self.assertEqual(self.p1, Point(new_point.x, 0), 'x coord should be stored and y coord should be set to 0')

        self.assertNotEqual(self.p1.y, new_point.y, 'y coords should not be equal before assignment')
        self.p1.assign(y=new_point.y)
        self.assertEqual(self.p1, Point(0, new_point.y), 'x coord should be set to 0 and y coord should be stored')

    # Tests for rotate
    def test_rotate_point_clockwise_around_origin(self):
        for p in (self.p0, self.p1, self.p2):
            with self.subTest(p=p):
                x, y = p.x, p.y
                p_temp = Point(x, y)
                p_temp.rotate(90, Point())
                self.assertAlmostEqual(p_temp.x, y, msg='should get correct x at 90 degrees clockwise rotation')
                self.assertAlmostEqual(p_temp.y, -x, msg='should get correct y at 90 degrees clockwise rotation')
                p_temp.rotate(90, Point())
                self.assertAlmostEqual(p_temp.x, -x, msg='should get correct x at 180 degrees clockwise rotation')
                self.assertAlmostEqual(p_temp.y, -y, msg='should get correct y at 180 degrees clockwise rotation')
                p_temp.rotate(90, Point())
                self.assertAlmostEqual(p_temp.x, -y, msg='should get correct x at 270 degrees clockwise rotation')
                self.assertAlmostEqual(p_temp.y, x, msg='should get correct y at 270 degrees clockwise rotation')
                p_temp.rotate(90, Point())
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x at 360 degrees clockwise rotation')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y at 360 degrees clockwise rotation')

    def test_rotate_point_counterclockwise_around_origin(self):
        for p in (self.p0, self.p1, self.p2):
            with self.subTest(p=p):
                x, y = p.x, p.y
                p_temp = Point(x, y)
                p_temp.rotate(-90, Point())
                self.assertAlmostEqual(p_temp.x, -y, msg='should get correct x at 90 degrees counterclockwise rotation')
                self.assertAlmostEqual(p_temp.y, x, msg='should get correct y at 90 degrees counterclockwise rotation')
                p_temp.rotate(-90, Point())
                self.assertAlmostEqual(p_temp.x, -x, msg='should get correct x at 180 degrees counterclockwise rotation')
                self.assertAlmostEqual(p_temp.y, -y, msg='should get correct y at 180 degrees counterclockwise rotation')
                p_temp.rotate(-90, Point())
                self.assertAlmostEqual(p_temp.x, y, msg='should get correct x at 270 degrees counterclockwise rotation')
                self.assertAlmostEqual(p_temp.y, -x, msg='should get correct y at 270 degrees counterclockwise rotation')
                p_temp.rotate(-90, Point())
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x at 360 degrees clockwise rotation')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y at 360 degrees clockwise rotation')

    def test_rotate_point_clockwise_around_itself(self):
        for p in (self.p0, self.p1, self.p2):
            with self.subTest(p=p):
                x, y = p.x, p.y
                p_temp = Point(x, y)
                p_temp.rotate(90, Point(x, y))
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x at 90 degrees clockwise rotation')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y at 90 degrees clockwise rotation')
                p_temp.rotate(90, Point(x, y))
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x at 90 degrees clockwise rotation')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y at 90 degrees clockwise rotation')
                p_temp.rotate(90, Point(x, y))
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x at 90 degrees clockwise rotation')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y at 90 degrees clockwise rotation')
                p_temp.rotate(90, Point(x, y))
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x at 90 degrees clockwise rotation')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y at 90 degrees clockwise rotation')

    def test_rotate_point_counterclockwise_around_itself(self):
        for p in (self.p0, self.p1, self.p2):
            with self.subTest(p=p):
                x, y = p.x, p.y
                p_temp = Point(x, y)
                p_temp.rotate(-90, Point(x, y))
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x at 90 degrees counterclockwise rotation')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y at 90 degrees counterclockwise rotation')
                p_temp.rotate(-90, Point(x, y))
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x at 90 degrees counterclockwise rotation')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y at 90 degrees counterclockwise rotation')
                p_temp.rotate(-90, Point(x, y))
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x at 90 degrees counterclockwise rotation')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y at 90 degrees counterclockwise rotation')
                p_temp.rotate(-90, Point(x, y))
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x at 90 degrees counterclockwise rotation')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y at 90 degrees counterclockwise rotation')

    def test_reflect_point_across_x_axis(self):
        for p in (self.p0, self.p1, self.p2):
            with self.subTest(p=p):
                x, y = p.x, p.y
                p_temp = Point(x, y)
                p_temp.rotate(180, Point(x, 0))
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x reflected across x axis')
                self.assertAlmostEqual(p_temp.y, -y, msg='should get correct y reflected across x axis')
                p_temp.rotate(180, Point(x, 0))
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x reflected across x axis')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y reflected across x axis')

    def test_reflect_point_across_y_axis(self):
        for p in (self.p0, self.p1, self.p2):
            with self.subTest(p=p):
                x, y = p.x, p.y
                p_temp = Point(x, y)
                p_temp.rotate(180, Point(0, y))
                self.assertAlmostEqual(p_temp.x, -x, msg='should get correct x reflected across y axis')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y reflected across y axis')
                p_temp.rotate(180, Point(0, y))
                self.assertAlmostEqual(p_temp.x, x, msg='should get correct x reflected across y axis')
                self.assertAlmostEqual(p_temp.y, y, msg='should get correct y reflected across y axis')

    # Tests for round
    def test_round_to_two_decimal_places(self):
        x, y = self.p0.x, self.p0.y
        self.p0.round(2)
        self.assertEqual(self.p0, Point(round(x, 2), round(y, 2)), 'should round point coords to two decimal places')

        x, y = self.p1.x, self.p1.y
        self.p1.round(2)
        self.assertEqual(self.p1, Point(round(x, 2), round(y, 2)), 'should round point coords to two decimal places')

        x, y = self.p2.x, self.p2.y
        self.p2.round(2)
        self.assertEqual(self.p2, Point(round(x, 2), round(y, 2)), 'should round point coords to two decimal places')

    # Tests for mult
    def test_scalar_multiplication(self):
        x, y = self.p0.x, self.p0.y
        self.p0.mult(3)
        self.assertEqual(self.p0, Point(x*3, y*3), 'should multiply point by positive integer')

        x, y = self.p1.x, self.p1.y
        self.p1.mult(-2)
        self.assertEqual(self.p1, Point(x*-2, y*-2), 'should multiply point by negative integer')

        x, y = self.p2.x, self.p2.y
        self.p2.mult(3.7)
        self.assertEqual(self.p2, Point(x*3.7, y*3.7), 'should multiply point by positive floating point')

if __name__ == '__main__':
    unittest.main()
