from math import hypot

from .point import Point

def boundary_box_check(tl, br, p):

    new_tl = Point(min(tl.x, p.x), max(tl.y, p.y))
    new_br = Point(max(br.x, p.x), min(br.y, p.y))

    return new_tl, new_br

def calculate_length_of_path_points(points_x, points_y):
    """
    Return the length of a path supplied in the form of x and y coordinate
    arrays
    """

    length = 0.0

    prev = Point(points_x[0], points_y[0])

    for i in range(1, len(points_x)):
        length += hypot(points_x[i] - prev.x, points_y[i] - prev.y)
        prev = Point(points_x[i], points_y[i])

    return length

def calculate_points_of_quadratic_bezier(p, steps = 10):
    """
    This function receives three points [start, control, end] and returns
    points on the quadratic Bezier curve that they define. It uses forward
    difference calculation the same way that calculate_points_of_cubic_bezier
    does.
    """

    t = 1.0 / steps
    t2 = t*t

    f = p[0]
    fd = 2*(p[1] - p[0]) * t
    fdd_per_2 = (p[0] - 2*p[1] + p[2]) * t2

    fdd = 2 * fdd_per_2

    points = []
    for x in range(steps):
        points.append(f)
        f += fd + fdd_per_2
        fd += fdd
    points.append(f)

    return points

def calculate_points_of_cubic_bezier(p, steps = 10):
    """
    This function receives four points [start, control, control, end]
    and returns points on the cubic Bezier curve that they define. As
    'steps' decreases, so do the amount of points that are returned,
    making the curve less, well, curvey.

    The code for this function was adapted/copied from:
    http://www.niksula.cs.hut.fi/~hkankaan/Homepages/bezierfast.html
    http://www.pygame.org/wiki/BezierCurve
    """

    t = 1.0 / steps
    temp = t*t

    f = p[0]
    fd = 3 * (p[1] - p[0]) * t
    fdd_per_2 = 3 * (p[0] - 2 * p[1] + p[2]) * temp
    fddd_per_2 = 3 * (3 * (p[1] - p[2]) + p[3] - p[0]) * temp * t

    fddd = 2 * fddd_per_2
    fdd = 2 * fdd_per_2
    fddd_per_6 = fddd_per_2 / 3.0

    points = []
    for x in range(steps):
        points.append(f)
        f += fd + fdd_per_2 + fddd_per_6
        fd += fdd + fddd_per_2
        fdd += fddd
        fdd_per_2 += fddd_per_2
    points.append(f)

    return points
