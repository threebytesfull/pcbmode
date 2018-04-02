#!/usr/bin/python

from math import sqrt, ceil
import pyparsing as PYP
import re

import pcbmode.config as config
from . import messages as msg

# import pcbmode modules
from . import utils
from pcbmode.utils.path_utils import boundary_box_check, calculate_points_of_quadratic_bezier, calculate_points_of_cubic_bezier, calculate_length_of_path_points, cubic_bezier_bounds, quadratic_bezier_bounds
from pcbmode.utils.svg_grammar import SvgGrammar
from .point import Point


class SvgPath():
    """
    """
    def __init__(self, path, gerber_lp=None):

        self._gerber_lp = gerber_lp

        self._original = path
        digest = utils.digest(path)
        self._record = config.pth.get(digest)

        self._svg_grammar = SvgGrammar().grammar

        if self._record == None:
            self._original_parsed = self.grammar.parseString(self._original)
            self._original_parsed = self._parseResultsToList(self._original_parsed)
            self._first_point = ([self._original_parsed[0][1][0],
                                  self._original_parsed[0][1][1]])
            self._relative = self._makeRelative(self._original_parsed)
            self._relative_parsed = self.grammar.parseString(self._relative)
            self._relative_parsed = self._parseResultsToList(self._relative_parsed)
            self._width, self._height = self._getDimensions(self._relative_parsed)
            config.pth[digest] = {}
            config.pth[digest]['first-point'] = self._first_point
            config.pth[digest]['relative'] = self._relative
            config.pth[digest]['relative-parsed'] = self._relative_parsed
            config.pth[digest]['width'] = self._width
            config.pth[digest]['height'] = self._height
            self._record = config.pth[digest]
        else:
            self._first_point = self._record['first-point']
            self._relative = self._record['relative']
            self._relative_parsed = self._record['relative-parsed']
            self._width = self._record['width']
            self._height = self._record['height']

    @property
    def grammar(self):
        return self._svg_grammar

    @property
    def top_left(self):
        return self._bbox_top_left

    @property
    def bottom_right(self):
        return self._bbox_bot_right




    def _parseResultsToList(self, parsed):
        """
        PyParsing returns an object that looks like a list, but isn't
        quite. For that reason it cannot be serialised and stored in a
        JSON file. This function converts it to a Python list
        """
        nl = []

        for cmd in parsed:
            lst = []
            lst.append(cmd[0])
            for coord in cmd[1:]:
                if len(coord) == 1:
                    lst.append([coord[0]])
                else:
                    lst.append([coord[0], coord[1]])
            nl.append(lst)

        return nl





    def getRelative(self):
        return self._relative


    def getRelativeParsed(self):
        return self._relative_parsed


    def getOriginal(self):
        return self._original

    def getFirstPoint(self):
        return self._first_point


    def getTransformed(self):
        return self._transformed


    def getTransformedMirrored(self):
        return self._transformed_mirrored


    def getWidth(self):
        return self._width


    def getHeight(self):
        return self._height



    def _makeRelative(self, path):
        """
        """

        p = ''

        # This variable stores the absolute coordinates as the path is converted;
        abspos = Point()

        patho = Point()

        for i in range(0, len(path)):

            command = path[i][0]
            command_lower = command.lower()

            # 'move to' command
            # M (x y)+
            if command_lower == 'm':

                # TODO: write this code more concisely

                coord = Point(path[i][1][0], path[i][1][1])
                p += 'm '

                # if this is the start of the path, the first M/m coordinate is
                # always absolute
                if i == 0:
                    abspos.assign(coord.x, coord.y)
                    p += str(abspos.x) + ',' + str(abspos.y) + ' '
                    patho.assign(coord.x, coord.y)
                else:
                    if path[i][0] == 'm':
                        p += str(coord.x) + ',' + str(coord.y) + ' '
                        abspos += coord
                        patho = abspos

                    else:
                        p += str(coord.x - abspos.x) + ',' + str(coord.y - abspos.y) + ' '
                        abspos.assign(coord.x, coord.y)
                        patho.assign(coord.x, coord.y)

                # do the rest of the coordinates
                for coord_tmp in path[i][2:]:
                    coord.assign(coord_tmp[0], coord_tmp[1])
                    if path[i][0] == 'm':
                        p += str(coord.x) + ',' + str(coord.y) + ' '
                        abspos += coord
                    else:
                        p += str(coord.x - abspos.x) + ',' + str(coord.y - abspos.y) + ' '
                        abspos.assign(coord.x, coord.y)


            # cubic Bezier (PCCP) curve command
            #    C (x1 y1 x2 y2 x y)+
            # -> C (control1 control2 dest)+
            elif command_lower == 'c':
                p += 'c '

                if command == 'c':
                    for coord_tmp in path[i][1:]:
                        coord.assign(coord_tmp[0], coord_tmp[1])
                        p += str(coord.x) + ',' + str(coord.y) +' '
                    # for keeping track of the absolute position, we need to add up every
                    # *third* coordinate of the cubic Bezier curve
                    for coord_tmp in path[i][3::3]:
                        coord.assign(coord_tmp[0], coord_tmp[1])
                        abspos += coord

                if command == 'C':
                    for n in range(1, len(path[i])-1, 3):
                        for m in range(0, 3):
                            coord.assign(path[i][n+m][0], path[i][n+m][1])
                            p += str(coord.x - abspos.x) + ',' + str(coord.y - abspos.y)+' '
                        abspos.assign(coord.x, coord.y)


            # quadratic Bezier (PCP) curve command
            #    Q (x1 y1 x y)+
            # -> Q (control1 dest)+
            elif command_lower == 'q':
                p += 'q '

                if command == 'q':
                    for coord_tmp in path[i][1:]:
                        coord.assign(coord_tmp[0], coord_tmp[1])
                        p += str(coord.x) + ',' + str(coord.y) +' '
                    # for keeping track of the absolute position, we need to add up every
                    # *second* coordinate of the quadratic Bezier curve
                    for coord_tmp in path[i][2::2]:
                        coord.assign(coord_tmp[0], coord_tmp[1])
                        abspos += coord

                if command == 'Q':
                    for j in range(1,len(path[i])+1, 2):
                        for coord_tmp in path[i][j:j+2]:
                            coord.assign(coord_tmp[0], coord_tmp[1])
                            p += str(coord.x - abspos.x) + ',' + str(coord.y - abspos.y) + ' '
                        abspos.assign(coord.x, coord.y)


            # simple quadratic Bezier curve command
            #    T (x y)+
            # -> T (dest)+
            elif command_lower == 't':
                p += 't '

                if command == 't':
                    for coord_tmp in path[i][1:]:
                        coord.assign(coord_tmp[0], coord_tmp[1])
                        p += str(coord.x) + ',' + str(coord.y) + ' '
                        # for keeping track of the absolute position, we need to add up every
                        # coordinate of the simple quadratic Bezier curve
                        abspos += coord

                if command == 'T':
                    for coord_tmp in path[i][1:]:
                        coord.assign(coord_tmp[0], coord_tmp[1])
                        p += str(coord.x - abspos.x) + ',' + str(coord.y - abspos.y) + ' '
                        abspos.assign(coord.x, coord.y)

            # simple cubic Bezier curve command
            #    S (x2 y2 x y)+
            # -> S (control2 dest)+
            elif command_lower == 's':
                p += 's '

                if command == 's':
                    for coord_tmp in path[i][1:]:
                        coord.assign(coord_tmp[0], coord_tmp[1])
                        p += str(coord.x)+','+str(coord.y)+' '
                        abspos += coord

                if command == 'S':
                    for j in range(1,len(path[i])+1, 2):
                        for coord_tmp in path[i][j:j+2]:
                            coord.assign(coord_tmp[0], coord_tmp[1])
                            p += str(coord.x - abspos.x) + ',' + str(coord.y - abspos.y) + ' '
                        abspos.assign(coord.x, coord.y)


            # 'line to'  command
            #    L (x y)+
            # -> L (dest)+
            elif command_lower == 'l':
                p += 'l '

                if command == 'l':
                    for coord_tmp in path[i][1:]:
                        coord.assign(coord_tmp[0], coord_tmp[1])
                        p += str(coord.x) + ',' + str(coord.y) + ' '
                        abspos += coord

                if command == 'L':
                    for coord_tmp in path[i][1:]:
                        coord.assign(coord_tmp[0], coord_tmp[1])
                        p += str(coord.x - abspos.x) + ',' + str(coord.y - abspos.y) + ' '
                        abspos.assign(coord.x, coord.y)


            # 'horizontal line' command
            #    H (x)+
            # -> H (dest_x)+
            elif command_lower == 'h':
                p += 'h '

                if command == 'h':
                    for coord_tmp in path[i][1:]:
                        coord.assign(coord_tmp[0], 0)
                        p += str(coord.x) + ' '
                    abspos.x += coord.x

                if command == 'H':
                    for coord_tmp in path[i][1:]:
                        coord.assign(coord_tmp[0], 0)
                        p += str(coord.x - abspos.x) + ' '
                        abspos.x = coord.x

            # 'vertical line' command
            #    V (y)+
            # -> V (dest_y)+
            elif command_lower == 'v':
                p += 'v '

                if command == 'v':
                    for coord_tmp in path[i][1:]:
                        coord.assign(0, coord_tmp[0])
                        p += str(coord.y) + ' '
                        abspos.y += coord.y

                if command == 'V':
                    for coord_tmp in path[i][1:]:
                        coord.assign(0, coord_tmp[0])
                        p += str(coord.y - abspos.y) + ' '
                        abspos.y = coord.y

            # 'close shape' command
            #    Z
            # -> Z
            elif command_lower == 'z':
                p += 'z '
                abspos = abspos + (patho - abspos) # TODO: just assign abspos = patho directly?

            else:
                msg.error("Found an unsupported SVG path command '%s' in _makeRelative" % path[i][0])


        return p






    def _mirrorHorizontally(self, path):
        """
        """

        p = ''

        for i in range(0, len(path)):

            pcmd = path[i][0]

            if re.match('m', pcmd):

                if i == 0:
                    p += 'm ' + str(-float(path[i][1][0])) + ',' + str(path[i][1][1]) + ' '
                else:
                    p += 'm ' + str(-float(path[i][1][0])) + ',' + str(path[i][1][1]) + ' '

                for coord in path[i][2:]:
                    p += str(-float(coord[0])) + ',' + coord[1] + ' '

            else:
                p += path[i][0]+' '
                for coord in path[i][1:]:
                    if len(coord) > 1:
                        p += str(-float(coord[0])) + ',' + str(float(coord[1])) + ' '
                    else:
                        if path[i][0] == 'h':
                            p += str(-float(coord[0])) + ' '
                        else:
                            p += str(float(coord[0])) + ' '

        return p



    def _getDimensions(self, path):
        """
        """

        last_point = Point()
        abs_point = Point()

        bbox_top_left = Point()
        bbox_bot_right = Point()

        # for the s/S/t/T (shorthand bezier) commands, we need to keep track
        # of the last bezier control point from previous C/c/S/s/Q/q/T/t command
        # TODO: check behaviour when non-Bezier command precedes shorthand bezier
        last_bezier_control_point = Point()

        for i in range(0, len(path)):

            command = path[i][0]

            # 'move to' command
            # m (dest)+
            if command == 'm':

                if i == 0:
                    # the first coordinate is the start of both top left and bottom right
                    abs_point.assign(path[i][1][0], path[i][1][1])
                    bbox_top_left.assign(path[i][1][0], path[i][1][1])
                    bbox_bot_right.assign(path[i][1][0], path[i][1][1])
                else:
                    new_point = Point(path[i][1][0], path[i][1][1])
                    abs_point += new_point
                    bbox_top_left, bbox_bot_right = boundary_box_check(bbox_top_left,
                                                                       bbox_bot_right,
                                                                       abs_point)

                # for the rest of the coordinates
                for coord in path[i][2:]:
                    new_point = Point(coord[0], coord[1])
                    abs_point += new_point
                    bbox_top_left, bbox_bot_right = boundary_box_check(bbox_top_left,
                                                                       bbox_bot_right,
                                                                       abs_point)

            # cubic Bezier curve command
            # c (control1 control2 dest)+
            elif command == 'c':

                bezier_curve_path = []

                for n in range(1, len(path[i])-1, 3):
                    bezier_curve_path.append(abs_point)
                    for m in range(0, 3):
                        coord = path[i][n+m]
                        point = Point(coord[0], coord[1])
                        bezier_curve_path.append(abs_point + point)
                    new_point = Point(path[i][n+m][0], path[i][n+m][1])
                    abs_point += new_point


                for n in range(0, len(bezier_curve_path), 4):

                    bezier_points_x, bezier_points_y = zip(*[(p.x, p.y) for p in bezier_curve_path[n:n+4]])
                    xmin, xmax = cubic_bezier_bounds(*bezier_points_x)
                    ymin, ymax = cubic_bezier_bounds(*bezier_points_y)
                    bbox_top_left, bbox_bot_right = boundary_box_check(
                        bbox_top_left,
                        bbox_bot_right,
                        Point(xmin, ymin))
                    bbox_top_left, bbox_bot_right = boundary_box_check(
                        bbox_top_left,
                        bbox_bot_right,
                        Point(xmax, ymax))


            # quadratic Bezier curve command
            # q (control1 dest)+
            elif command == 'q':

                bezier_curve_path = []

                for n in range(1, len(path[i])-1, 2):
                    bezier_curve_path.append(abs_point)
                    for m in range(0, 2):
                        coord = path[i][n+m]
                        point = Point(coord[0], coord[1])
                        bezier_curve_path.append(abs_point + point)
                        if m == 0:
                            last_bezier_control_point = abs_point + point
                    new_point = Point(path[i][n+m][0], path[i][n+m][1])
                    abs_point += new_point


                for n in range(0, len(bezier_curve_path), 3):

                    bezier_points_x, bezier_points_y = zip(*[(p.x, p.y) for p in bezier_curve_path[n:n+3]])
                    xmin, xmax = quadratic_bezier_bounds(*bezier_points_x)
                    ymin, ymax = quadratic_bezier_bounds(*bezier_points_y)
                    bbox_top_left, bbox_bot_right = boundary_box_check(
                        bbox_top_left,
                        bbox_bot_right,
                        Point(xmin, ymin))
                    bbox_top_left, bbox_bot_right = boundary_box_check(
                        bbox_top_left,
                        bbox_bot_right,
                        Point(xmax, ymax))


            # simple quadratic Bezier curve command
            # t (dest)+
            elif command == 't':
                bezier_curve_path = []

                for n in range(1, len(path[i])):
                    bezier_curve_path.append(abs_point)
                    coord = path[i][n]
                    point = Point(coord[0], coord[1])
                    end_point = abs_point + point
                    # construct control point by reflecting through current point
                    diff = Point(abs_point.x - last_bezier_control_point.x,
                                 abs_point.y - last_bezier_control_point.y)
                    control_point = abs_point + diff
                    bezier_curve_path.append(control_point)
                    bezier_curve_path.append(end_point)
                    last_bezier_control_point = control_point
                    new_point = Point(path[i][n][0], path[i][n][1])
                    abs_point += new_point


                for n in range(0, len(bezier_curve_path), 3):

                    bezier_points_x, bezier_points_y = zip(*[(p.x, p.y) for p in bezier_curve_path[n:n+3]])
                    xmin, xmax = quadratic_bezier_bounds(*bezier_points_x)
                    ymin, ymax = quadratic_bezier_bounds(*bezier_points_y)
                    bbox_top_left, bbox_bot_right = boundary_box_check(
                        bbox_top_left,
                        bbox_bot_right,
                        Point(xmin, ymin))
                    bbox_top_left, bbox_bot_right = boundary_box_check(
                        bbox_top_left,
                        bbox_bot_right,
                        Point(xmax, ymax))



            # simple cubic Bezier curve command
            elif command == 's':
                bezier_curve_path = []

                for n in range(1, len(path[i])):
                    bezier_curve_path.append(abs_point)
                    coord = path[i][n]
                    point = Point(coord[0], coord[1])
                    end_point = abs_point + point
                    # construct control point by reflecting through current point
                    diff = Point(abs_point.x - last_bezier_control_point.x,
                                 abs_point.y - last_bezier_control_point.y)
                    control_point = abs_point + diff
                    bezier_curve_path.append(control_point)
                    bezier_curve_path.append(end_point)
                    bezier_curve_path.append(end_point)
                    last_bezier_control_point = control_point
                    new_point = Point(path[i][n][0], path[i][n][1])
                    abs_point += new_point


                for n in range(0, len(bezier_curve_path), 4):

                    bezier_points_x, bezier_points_y = zip(*[(p.x, p.y) for p in bezier_curve_path[n:n+3]])
                    xmin, xmax = quadratic_bezier_bounds(*bezier_points_x)
                    ymin, ymax = quadratic_bezier_bounds(*bezier_points_y)
                    bbox_top_left, bbox_bot_right = boundary_box_check(
                        bbox_top_left,
                        bbox_bot_right,
                        Point(xmin, ymin))
                    bbox_top_left, bbox_bot_right = boundary_box_check(
                        bbox_top_left,
                        bbox_bot_right,
                        Point(xmax, ymax))


            # 'line to'  command
            elif command == 'l':
                for coord in path[i][1:]:
                    new_point = Point(coord[0], coord[1])
                    abs_point += new_point
                    bbox_top_left, bbox_bot_right = boundary_box_check(bbox_top_left,
                                                                       bbox_bot_right,
                                                                       abs_point)

            # 'horizontal line' command
            elif command == 'h':
                for coord in path[i][1:]:
                    new_point = Point(coord[0], 0)
                    abs_point += new_point
                    bbox_top_left, bbox_bot_right = boundary_box_check(bbox_top_left,
                                                                       bbox_bot_right,
                                                                       abs_point)

            # 'vertical line' command
            elif command == 'v':
                for coord in path[i][1:]:
                    new_point = Point(0, coord[0])
                    abs_point += new_point
                    bbox_top_left, bbox_bot_right = boundary_box_check(bbox_top_left,
                                                                       bbox_bot_right,
                                                                       abs_point)

            # 'close shape' command
            elif command == 'z':
                pass

            else:
                print("ERROR: found an unsupported SVG path command {} in _getDimensions".format(str(path[i][0])))

        self._bbox_top_left = bbox_top_left
        self._bbox_bot_right = bbox_bot_right
        #self._width = (bbox_bot_right.x - bbox_top_left.x)
        #self._height = abs(bbox_bot_right.y - bbox_top_left.y)
        return (bbox_bot_right.x - bbox_top_left.x), abs(bbox_bot_right.y - bbox_top_left.y)





    def transform(self, scale=1, rotate_angle=0, rotate_point=Point(), mirror=False, center=True):
        """
        Transforms a path
        """

        path = self._relative_parsed

        string = "%s%s%s%s%s%s" % (path,scale,rotate_angle,rotate_point,mirror,center)
        digest = utils.digest(string)

        record = self._record.get(digest)
        if record != None:
            self._transformed = record['path']
            self._transformed_mirrored = record['mirrored']
            self._width = record['width']
            self._height = record['height']
        else:
            width, height = self._getDimensions(path)

            # first point of path
            first_point = Point(path[0][1][0], path[0][1][1])

            if center is True:
                # center point of path
                origin_point = Point(self._bbox_top_left.x+width/2, self._bbox_top_left.y-height/2)

                # calculate what's the new starting point of path based on the new origin
                new_first_point = Point(first_point.x - origin_point.x, first_point.y - origin_point.y)
            else:
                new_first_point = Point(first_point.x, first_point.y)

            new_first_point.rotate(rotate_angle, rotate_point)
            new_first_point.mult(scale)
            new_p = "m %f,%f " % (new_first_point.x, new_first_point.y)

            tmpp = Point()
            origin = Point()

            for n in range(0, len(path)):
                if path[n][0] == 'm' and n == 0:
                    for m in range(2, len(path[n])):
                        tmpp.assign(path[n][m][0], path[n][m][1])
                        tmpp.rotate(rotate_angle, rotate_point)
                        tmpp.mult(scale)
                        new_p += str(tmpp.x) + "," + str(tmpp.y) + " "
                else:
                    if path[n][0] == 'h' or path[n][0] == 'v':
                        new_p += "l "
                    else:
                        new_p += path[n][0] + " "

                    for m in range(1, len(path[n])):
                        if path[n][0] == 'h':
                            tmpp.assign(path[n][m][0], 0)
                        elif path[n][0] == 'v':
                            tmpp.assign(0, path[n][m][0])
                        else:
                            tmpp.assign(path[n][m][0], path[n][m][1])

                        tmpp.rotate(rotate_angle, rotate_point)
                        tmpp.mult(scale)
                        new_p += str(tmpp.x) + "," + str(tmpp.y) + " "


            parsed = self.grammar.parseString(new_p)
            mirrored = self._mirrorHorizontally(parsed)

            if mirror == False:
                self._transformed_mirrored = mirrored
                self._transformed = new_p
            else:
                self._transformed_mirrored = new_p
                self._transformed = mirrored

            width, height = self._getDimensions(parsed)
            self._width = width
            self._height = height

            self._record[digest] = {}

            self._record[digest]['path'] = self._transformed
            self._record[digest]['mirrored'] = self._transformed_mirrored

            self._record[digest]['width'] = self._width
            self._record[digest]['height'] = self._height

        return





    def getCoordList(self, steps, length):
        return self._makeCoordList(self._relative_parsed, steps, length)






    def _makeCoordList(self, path, steps, length):
        """
        """

        # absolute position
        ap = Point()

        # path origin
        po = Point()

        points = []
        p = []

        # TODO: legacy
        pd = path

        # for the s/S/t/T (shorthand bezier) commands, we need to keep track
        # of the last bezier control point from previous C/c/S/s/Q/q/T/t command
        # TODO: check behaviour when non-Bezier command precedes shorthand bezier
        last_bezier_control_point = Point()

        for i in range(0, len(pd)):

            cmd = pd[i][0]

            # 'move to' command
            if re.match('m', cmd):
                if i == 0:
                    coord = Point(pd[i][1][0], pd[i][1][1])
                    ap.assign(coord.x, coord.y)
                    p.append(ap)
                    po.assign(coord.x, coord.y)
                else:
                    coord_tmp = Point(pd[i][1][0], pd[i][1][1])
                    ap += coord_tmp
                    # a marker that a new path is starting after a previous one closed
                    points.append(p)
                    p = []
                    p.append(ap)
                    po = ap

                for coord_tmp in pd[i][2:]:
                    coord = Point(coord_tmp[0], coord_tmp[1])
                    ap += coord
                    p.append(ap)

            # cubic (two control points) Bezier curve command
            elif re.match('c', cmd):

                bezier_curve_path = []

                for n in range(1, len(pd[i])-1, 3):
                    bezier_curve_path.append(ap)
                    for m in range(0, 3):
                        coord = pd[i][n+m]
                        point = Point(coord[0], coord[1])
                        bezier_curve_path.append(ap + point)
                    new_point = Point(pd[i][n+m][0], pd[i][n+m][1])
                    ap += new_point


                for n in range(0, len(bezier_curve_path), 4):

                    # clear bezier point arrays
                    bezier_points_x = []
                    bezier_points_y = []

                    # split points of bezier into 'x' and 'y' coordinate arrays
                    # as this is what the point array function expects
                    for m in range(0, 4):
                        bezier_points_x.append(bezier_curve_path[n+m].x)
                        bezier_points_y.append(bezier_curve_path[n+m].y)


                    # calculate the individual points along the bezier curve for 'x'
                    # and 'y'
                    points_x = calculate_points_of_cubic_bezier(bezier_points_x, steps)
                    points_y = calculate_points_of_cubic_bezier(bezier_points_y, steps)

                    path_length = calculate_length_of_path_points(points_x, points_y)

                    if path_length == 0:
                        steps_tmp = 1
                    else:
                        steps_tmp = ceil(path_length / length)
                    skip = int(ceil(steps / steps_tmp))

                    bezier_point_array = []

                    # put those points back into a Point type array
                    for n in range(0, len(points_x), skip):
                        bezier_point_array.append(Point(points_x[n], points_y[n]))
                    bezier_point_array.append(Point(points_x[len(points_x)-1], points_y[len(points_x)-1]))

                    p += bezier_point_array


            # quadratic (single control point) Bezier curve command
            elif re.match('q', cmd):

                bezier_curve_path = []

                for n in range(1, len(pd[i])-1, 2):
                    bezier_curve_path.append(ap)
                    for m in range(0, 2):
                        coord = pd[i][n+m]
                        point = Point(coord[0], coord[1])
                        bezier_curve_path.append(ap + point)
                        if m == 0:
                            last_bezier_control_point = ap + point
                    new_point = Point(pd[i][n+m][0], pd[i][n+m][1])
                    ap += new_point


                for n in range(0, len(bezier_curve_path), 3):

                    # clear bezier point arrays
                    bezier_points_x = []
                    bezier_points_y = []

                    # split points of bezier into 'x' and 'y' coordinate arrays
                    # as this is what the point array function expects
                    for m in range(0, 3):
                        bezier_points_x.append(bezier_curve_path[n+m].x)
                        bezier_points_y.append(bezier_curve_path[n+m].y)


                    # calculate the individual points along the bezier curve for 'x'
                    # and 'y'
                    points_x = calculate_points_of_quadratic_bezier(bezier_points_x, steps)
                    points_y = calculate_points_of_quadratic_bezier(bezier_points_y, steps)

                    path_length = calculate_length_of_path_points(points_x, points_y)
                    skip = int(ceil(steps / (path_length / length)))

                    bezier_point_array = []

                    # put those points back into a Point type array
                    for n in range(0, len(points_x), skip):
                        bezier_point_array.append(Point(points_x[n], points_y[n]))
                    bezier_point_array.append(Point(points_x[len(points_x)-1], points_y[len(points_x)-1]))

                    p += bezier_point_array



            # simple cubic Bezier curve command
            elif re.match('t', cmd):

                bezier_curve_path = []

                for n in range(1, len(pd[i])):
                    bezier_curve_path.append(ap)
                    coord = pd[i][n]
                    point = Point(coord[0], coord[1])
                    end_point = ap + point
                    diff = Point(ap.x - last_bezier_control_point.x, ap.y - last_bezier_control_point.y)
                    control_point = ap + diff
                    bezier_curve_path.append(control_point)
                    bezier_curve_path.append(end_point)
                    bezier_curve_path.append(end_point)
                    last_bezier_control_point = control_point
                    new_point = Point(pd[i][n][0], pd[i][n][1])
                    ap += new_point

                for n in range(0, len(bezier_curve_path), 4):

                    # clear bezier point arrays
                    bezier_points_x = []
                    bezier_points_y = []

                    # split points of bezier into 'x' and 'y' coordinate arrays
                    # as this is what the point array function expects
                    for m in range(0, 4):
                        bezier_points_x.append(bezier_curve_path[n+m].x)
                        bezier_points_y.append(bezier_curve_path[n+m].y)

                    # calculate the individual points along the bezier curve for 'x'
                    # and 'y'
                    points_x = calculate_points_of_cubic_bezier(bezier_points_x, steps)
                    points_y = calculate_points_of_cubic_bezier(bezier_points_y, steps)

                    path_length = calculate_length_of_path_points(points_x, points_y)
                    skip = int(ceil(steps / (path_length / length)))

                    bezier_point_array = []

                    # put those points back into a Point type array
                    for m in range(0, len(points_x), skip):
                        bezier_point_array.append(Point(points_x[m], points_y[m]))
                    bezier_point_array.append(Point(points_x[len(points_x)-1], points_y[len(points_x)-1]))

                    p += bezier_point_array


    #        elif re.match('s', cmd):
    #            pass

            # 'line to'  command
            elif re.match('l', cmd):
                for coord_tmp in pd[i][1:]:
                    coord = Point(coord_tmp[0], coord_tmp[1])
                    ap += coord
                    p.append(ap)

            # 'horizontal line' command
            elif re.match('h', cmd):
                for coord_tmp in pd[i][1:]:
                    coord = Point(coord_tmp[0], 0)
                    ap += coord
                    p.append(ap)

            # 'vertical line' command
            elif re.match('v', cmd):
                for coord_tmp in pd[i][1:]:
                    coord = Point(0, coord_tmp[0])
                    ap += coord
                    p.append(ap)

            # 'close shape' command
            elif re.match('z', cmd):
                ap = ap + (po - ap)


            else:
                msg.error("Found an unsupported SVG path command, '%s' in _makeCoordList" % cmd)


        points.append(p)

        return points






    def getNumberOfSegments(self):
        """
        """
        return self._relative.lower().count('m')
