import pyparsing as PP

from pcbmode.utils.point import Point

class SvgParser(object):

    @classmethod
    def grammar(cls):

        to_int = lambda s,l,t: [ int(t[0]) ]
        to_float = lambda s,l,t: [ float(t[0]) ]
        to_bool = lambda s,l,t: [ bool(int(t[0])) ]
        to_point = lambda s,l,t: [ Point(t[0], t[1]) ]

        wsp = PP.Word(' \t\r\n').suppress()
        opt_wsp = PP.Optional(wsp)

        digit_sequence = PP.Word(PP.nums)
        sign = PP.oneOf('+ -')
        exponent = PP.Combine(PP.oneOf('E e') + PP.Optional(sign) + digit_sequence)
        fractional_constant = PP.Combine(PP.Optional(digit_sequence) + PP.Literal('.') + digit_sequence) ^ PP.Combine(digit_sequence + PP.Literal('.'))
        floating_point_constant = PP.Combine(fractional_constant + PP.Optional(exponent)) ^ PP.Combine(digit_sequence + PP.Optional(exponent))
        integer_constant = digit_sequence

        comma = PP.Literal(',').suppress()
        comma_wsp = PP.Combine(PP.OneOrMore(wsp) + PP.Optional(comma) + opt_wsp).suppress() ^ PP.Combine(comma + opt_wsp).suppress()
        opt_comma_wsp = PP.Optional(comma_wsp)

        flag = PP.oneOf('0 1')
        flag.setParseAction(to_bool)

        number_int = PP.Combine(PP.Optional(sign) + integer_constant)
        number_int.setParseAction(to_int)

        number_float = PP.Combine(PP.Optional(sign) + floating_point_constant)
        number_float.setParseAction(to_float)

        number = number_int ^ number_float

        nonnegative_number_int = integer_constant
        nonnegative_number_int.setParseAction(to_int)

        nonnegative_number_float = floating_point_constant
        nonnegative_number_float.setParseAction(to_float)

        nonnegative_number = nonnegative_number_int ^ nonnegative_number_float

        coordinate = number
        coordinate_pair = PP.Group(coordinate + opt_comma_wsp + coordinate)
        coordinate_pair = coordinate + opt_comma_wsp + coordinate
        coordinate_pair.setParseAction(to_point)

        elliptical_arc_argument = PP.Group(nonnegative_number + opt_comma_wsp + nonnegative_number + opt_comma_wsp + number + opt_comma_wsp + flag + opt_comma_wsp + flag + opt_comma_wsp + coordinate_pair)
        elliptical_arc_argument_sequence = elliptical_arc_argument + PP.ZeroOrMore(opt_comma_wsp + elliptical_arc_argument)
        elliptical_arc = PP.oneOf('A a') + opt_wsp + elliptical_arc_argument_sequence

        smooth_quadratic_bezier_curveto_argument_sequence = coordinate_pair + PP.ZeroOrMore(opt_comma_wsp + coordinate_pair)
        smooth_quadratic_bezier_curveto = PP.oneOf('T t') + opt_wsp + smooth_quadratic_bezier_curveto_argument_sequence

        quadratic_bezier_curveto_argument = PP.Group(coordinate_pair + opt_comma_wsp + coordinate_pair)
        quadratic_bezier_curveto_argument_sequence = quadratic_bezier_curveto_argument + PP.ZeroOrMore(opt_comma_wsp + quadratic_bezier_curveto_argument)
        quadratic_bezier_curveto = PP.oneOf('Q q') + opt_wsp + quadratic_bezier_curveto_argument_sequence

        smooth_curveto_argument = PP.Group(coordinate_pair + opt_comma_wsp + coordinate_pair)
        smooth_curveto_argument_sequence = smooth_curveto_argument + PP.ZeroOrMore(opt_comma_wsp + smooth_curveto_argument)
        smooth_curveto = PP.oneOf('S s') + opt_wsp + smooth_curveto_argument_sequence

        curveto_argument = PP.Group(coordinate_pair + opt_comma_wsp + coordinate_pair + opt_comma_wsp + coordinate_pair)
        curveto_argument_sequence = curveto_argument + PP.ZeroOrMore(opt_comma_wsp + curveto_argument)
        curveto = PP.oneOf('C c') + opt_wsp + curveto_argument_sequence

        vertical_lineto_argument_sequence = coordinate + PP.ZeroOrMore(opt_comma_wsp + coordinate)
        vertical_lineto = PP.oneOf('V v') + opt_wsp + vertical_lineto_argument_sequence

        horizontal_lineto_argument_sequence = coordinate + PP.ZeroOrMore(opt_comma_wsp + coordinate)
        horizontal_lineto = PP.oneOf('H h') + opt_wsp + horizontal_lineto_argument_sequence

        lineto_argument_sequence = coordinate_pair + PP.ZeroOrMore(opt_comma_wsp + coordinate_pair)
        lineto = PP.oneOf('L l') + opt_wsp + lineto_argument_sequence

        closepath = PP.oneOf('Z z')

        moveto_argument_sequence = coordinate_pair ^ (coordinate_pair + opt_comma_wsp + lineto_argument_sequence)
        moveto = PP.oneOf('M m') + opt_wsp + moveto_argument_sequence

        drawto_command = closepath ^ lineto ^ horizontal_lineto ^ vertical_lineto ^ curveto ^ smooth_curveto ^ quadratic_bezier_curveto ^ smooth_quadratic_bezier_curveto ^ elliptical_arc
        drawto_commands = drawto_command + PP.ZeroOrMore(opt_wsp + drawto_command)

        moveto_drawto_command_group = moveto + opt_wsp + PP.Optional(drawto_commands)
        moveto_drawto_command_groups = moveto_drawto_command_group + PP.ZeroOrMore(opt_wsp + moveto_drawto_command_group)

        svg_path = opt_wsp + PP.Optional(moveto_drawto_command_groups) + opt_wsp

        return svg_path
