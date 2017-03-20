import pyparsing as PP

class SvgGrammar(object):

    class __SvgGrammar:
        def __init__(self):
            # pyparsing grammar
            comma = PP.Literal(",").suppress() # supress removes the ',' when captured
            dot = PP.Literal(".")
            coord = PP.Regex(r"-?\d+(\.\d*)?([Ee][+-]?\d+)?")
            one_coord = PP.Group(coord)
            xycoords = PP.Group(coord + PP.Optional(comma) + coord)
            two_xycoords = xycoords + PP.Optional(comma) + xycoords
            three_xycoords = xycoords + PP.Optional(comma) + xycoords + PP.Optional(comma)+xycoords

            # TODO optimise this; there has to be a more efficient way to describe this
            c_M = PP.Literal('M') + PP.OneOrMore(xycoords)
            c_m = PP.Literal('m') + PP.OneOrMore(xycoords)

            c_C = PP.Literal('C') + PP.OneOrMore(three_xycoords)
            c_c = PP.Literal('c') + PP.OneOrMore(three_xycoords)

            c_Q = PP.Literal('Q') + PP.OneOrMore(two_xycoords)
            c_q = PP.Literal('q') + PP.OneOrMore(two_xycoords)

            c_T = PP.Literal('T') + PP.OneOrMore(xycoords)
            c_t = PP.Literal('t') + PP.OneOrMore(xycoords)

            c_L = PP.Literal('L') + PP.OneOrMore(xycoords)
            c_l = PP.Literal('l') + PP.OneOrMore(xycoords)

            c_V = PP.Literal('V') + PP.OneOrMore(one_coord)
            c_v = PP.Literal('v') + PP.OneOrMore(one_coord)

            c_H = PP.Literal('H') + PP.OneOrMore(one_coord)
            c_h = PP.Literal('h') + PP.OneOrMore(one_coord)

            c_S = PP.Literal('S') + PP.OneOrMore(two_xycoords)
            c_s = PP.Literal('s') + PP.OneOrMore(two_xycoords)

            c_z = PP.Literal('z')
            c_Z = PP.Literal('Z')

            path_cmd = c_M | c_m | c_C | c_c | c_Q | c_q | c_T | c_t | c_L | c_l | c_V | c_v | c_H | c_h | c_S | c_s | c_Z | c_z

            self.grammar = PP.OneOrMore(PP.Group(path_cmd))

    instance = None

    def __new__(cls):
        if not SvgGrammar.instance:
            SvgGrammar.instance = SvgGrammar.__SvgGrammar()
        return SvgGrammar.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)

    @property
    def grammar(self):
        return self.instance.grammar
