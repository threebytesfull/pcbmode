import pyparsing as PP

from pcbmode.utils.point import Point

def _svg_a(s, l, t):
    # A (rx ry x_axis_rotation large_arc_flag sweep_flag x y)+
    command, *args = t[0]
    segments = [{ 'rx': a[0], 'ry': a[1], 'x_axis_rotation': a[2], 'large_arc_flag': a[3], 'sweep_flag': a[4], 'destination': a[5] } for a in args]
    return {
        'type': 'arcto',
        'absolute': command.isupper(),
        'segments': segments,
    }

def _svg_t(s, l, t):
    # T (x y)+
    command, *args = t[0]
    return {
        'type': 'smooth_quadratic_curveto',
        'absolute': command.isupper(),
        'segments': args,
    }

def _svg_q(s, l, t):
    # Q (x1 y1 x y)+
    command, *args = t[0]
    sgements = [{'control': a[0], 'destination': a[1]} for a in args]
    return {
        'type': 'quadratic_curveto',
        'absolute': command.isupper(),
        'segments': segments,
    }

def _svg_s(s, l, t):
    # S (x2 y2 x y)+
    command, *args = t[0]
    segments = [{'control': a[0], 'destination': a[1]} for a in args]
    return {
        'type': 'smooth_curveto',
        'absolute': command.isupper(),
        'segments': segments,
    }

def _svg_c(s, l, t):
    # C (x1 y1 x2 y2 x y)+
    command, *args = t[0]
    segments = [{'control1': a[0], 'control2': a[1], 'destination': a[2]} for a in args]
    return {
        'type': 'curveto',
        'absolute': command.isupper(),
        'segments': segments,
    }

def _svg_v(s, l, t):
    # V y+
    command, *args = t[0]
    return {
        'type': 'vertical_lineto',
        'absolute': command.isupper(),
        'segments': args,
    }

def _svg_h(s, l, t):
    # H x+
    command, *args = t[0]
    return {
        'type': 'horizontal_lineto',
        'absolute': command.isupper(),
        'segments': args,
    }

def _svg_l(s, l, t):
    # L (x y)+
    command, *args = t[0]
    return {
        'type': 'lineto',
        'absolute': command.isupper(),
        'segments': args,
    }

def _svg_z(s, l, t):
    # Z
    command, *args = t[0]
    return {
        'type': 'closepath',
    }

def _svg_m(s, l, t):
    # M (x y)+
    command, *args = t[0]
    return {
        'type': 'moveto',
        'absolute': command.isupper(),
        'segments': args,
    }

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
        elliptical_arc = PP.Group(PP.oneOf('A a') + opt_wsp + elliptical_arc_argument_sequence)
        elliptical_arc.setParseAction(_svg_a)

        smooth_quadratic_bezier_curveto_argument_sequence = coordinate_pair + PP.ZeroOrMore(opt_comma_wsp + coordinate_pair)
        smooth_quadratic_bezier_curveto = PP.Group(PP.oneOf('T t') + opt_wsp + smooth_quadratic_bezier_curveto_argument_sequence)
        smooth_quadratic_bezier_curveto.setParseAction(_svg_t)

        quadratic_bezier_curveto_argument = PP.Group(coordinate_pair + opt_comma_wsp + coordinate_pair)
        quadratic_bezier_curveto_argument_sequence = quadratic_bezier_curveto_argument + PP.ZeroOrMore(opt_comma_wsp + quadratic_bezier_curveto_argument)
        quadratic_bezier_curveto = PP.Group(PP.oneOf('Q q') + opt_wsp + quadratic_bezier_curveto_argument_sequence)
        quadratic_bezier_curveto.setParseAction(_svg_q)

        smooth_curveto_argument = PP.Group(coordinate_pair + opt_comma_wsp + coordinate_pair)
        smooth_curveto_argument_sequence = smooth_curveto_argument + PP.ZeroOrMore(opt_comma_wsp + smooth_curveto_argument)
        smooth_curveto = PP.Group(PP.oneOf('S s') + opt_wsp + smooth_curveto_argument_sequence)
        smooth_curveto.setParseAction(_svg_s)

        curveto_argument = PP.Group(coordinate_pair + opt_comma_wsp + coordinate_pair + opt_comma_wsp + coordinate_pair)
        curveto_argument_sequence = curveto_argument + PP.ZeroOrMore(opt_comma_wsp + curveto_argument)
        curveto = PP.Group(PP.oneOf('C c') + opt_wsp + curveto_argument_sequence)
        curveto.setParseAction(_svg_c)

        vertical_lineto_argument_sequence = coordinate + PP.ZeroOrMore(opt_comma_wsp + coordinate)
        vertical_lineto = PP.Group(PP.oneOf('V v') + opt_wsp + vertical_lineto_argument_sequence)
        vertical_lineto.setParseAction(_svg_v)

        horizontal_lineto_argument_sequence = coordinate + PP.ZeroOrMore(opt_comma_wsp + coordinate)
        horizontal_lineto = PP.Group(PP.oneOf('H h') + opt_wsp + horizontal_lineto_argument_sequence)
        horizontal_lineto.setParseAction(_svg_h)

        lineto_argument_sequence = coordinate_pair + PP.ZeroOrMore(opt_comma_wsp + coordinate_pair)
        lineto = PP.Group(PP.oneOf('L l') + opt_wsp + lineto_argument_sequence)
        lineto.setParseAction(_svg_l)

        closepath = PP.Group(PP.oneOf('Z z'))
        closepath.setParseAction(_svg_z)

        moveto_argument_sequence = coordinate_pair ^ (coordinate_pair + opt_comma_wsp + lineto_argument_sequence)
        moveto = PP.Group(PP.oneOf('M m') + opt_wsp + moveto_argument_sequence)
        moveto.setParseAction(_svg_m)

        drawto_command = closepath ^ lineto ^ horizontal_lineto ^ vertical_lineto ^ curveto ^ smooth_curveto ^ quadratic_bezier_curveto ^ smooth_quadratic_bezier_curveto ^ elliptical_arc
        drawto_commands = drawto_command + PP.ZeroOrMore(opt_wsp + drawto_command)

        moveto_drawto_command_group = moveto + opt_wsp + PP.Optional(drawto_commands)
        moveto_drawto_command_groups = moveto_drawto_command_group + PP.ZeroOrMore(opt_wsp + moveto_drawto_command_group)

        svg_path = opt_wsp + PP.Optional(moveto_drawto_command_groups) + opt_wsp

        return svg_path
