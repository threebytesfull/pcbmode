from math import hypot, sqrt

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

def quadratic_bezier_bounds(start, control, end):
    min_end = min(start, end)
    max_end = max(start, end)

    if control < min_end or control > max_end:
        denom = 2*control - start - end
        t = (control - start) / denom
        if t >= 0 and t <= 1:
            t2 = t*t
            lim = start*(t2-2*t+1) + control*(-2*t2+2*t) + end*t2
            min_end = min(min_end, lim)
            max_end = max(max_end, lim)

    return min_end, max_end

def cubic_bezier_bounds(start, control1, control2, end):
    min_end = min(start, end)
    max_end = max(start, end)

    def __cubic_value_at(t):
        a = -start + 3*control1 - 3*control2 + end
        b = 3*start - 6*control1 + 3*control2
        c = -3*start + 3*control1
        d = start

        t2=t*t
        t3=t2*t

        return a*t3 + b*t2 + c*t + d

    first_a = -3*start + 9*control1 - 9*control2 + 3*end
    first_b = 6*start - 12*control1 + 6*control2
    first_c = -3*start + 3*control1

    discrim = first_b*first_b - 4*first_a*first_c

    if first_a == 0:
        # no cubic coefficient, so it's actually a quadratic curve
        # we can ignore first term of the derivative and just solve linear equation
        num = -first_c
        denom = first_b
        if denom != 0:
            t = num / denom
            if t >= 0 and t <= 1:
                lim = __cubic_value_at(t)
                min_end = min(min_end, lim)
                max_end = max(max_end, lim)
    else:
        # cubic curve
        if discrim >= 0:
            denom = 2*first_a
            if discrim == 0:
                # only one solution
                t = -first_b/denom
                if t >=0 and t <=1:
                    # get lim at t
                    lim = __cubic_value_at(t)
                    min_end = min(min_end, lim)
                    max_end = max(max_end, lim)
            else:
                # two solutions
                root_discrim = sqrt(discrim)
                t1 = (-first_b + root_discrim) / denom
                t2 = (-first_b - root_discrim) / denom
                for t in [t_ for t_ in (t1, t2) if t_>=0 and t_<=1]:
                    # calculate lim at this t
                    second_a = -6*start + 18*control1 - 18*control2 + 6*end
                    second_b = 6*start - 12*control1 + 6*control2

                    second_derivative = t*second_a + second_b
                    lim = __cubic_value_at(t)

                    if second_derivative > 0:
                        # concave up, so this is a minimum
                        min_end = min(min_end, lim)
                    elif second_derivative < 0:
                        # concave down, so this is a maximum
                        max_end = max(max_end, lim)

    return min_end, max_end
