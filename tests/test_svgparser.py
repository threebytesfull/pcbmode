try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pcbmode.utils.svgparser import SvgParser

g = SvgParser.grammar()

class TestSvgParser(unittest.TestCase):

    def test_parse_example_paths(self):
        paths = [
            'M3,4z',
            'm5,6z',
            'm1,5 6,7 8,9 z',
            'M600,350 l 50,-25',
            'm0 0 a10,10 10 0 0 10,10',
            'm0,0t1,2,3,4,5,6',
            # Examples from SVG spec path discussion
            'M100,200 C100,100 250,100 250,200 S400,300 400,200',
            'M100,200 C100,100 400,100 400,200',
            'M600,200 C675,100 975,100 900,200',
            'M100,500 C25,400 475,400 400,500',
            'M600,500 C600,350 900,650 900,500',
            'M100,800 C175,700 325,700 400,800',
            'M600,800 C625,700 725,700 750,800 S875,900 900,800',
            'M200,300 Q400,50 600,300 T1000,300 M200,300 L400,50 L600,300 L800,550 L1000,300',
            'M300,200 h-150 a150,150 0 1,0 150,-150 z',
            'M600,350 l 50,-25 a25,25 -30 0,1 50,-25 l 50,-25 a25,50 -30 0,1 50,-25 l 50,-25 a25,75 -30 0,1 50,-25 l 50,-25 a25,100 -30 0,1 50,-25 l 50,-25',
        ]
        for path in paths:
            with self.subTest(path=path):
                result = g.parseString(path, parseAll=True)

    def test_parse_path_fails_without_initial_move(self):
        with self.assertRaises(Exception):
            g.parseString('L3,3', parseAll=True)
        res = g.parseString('M0,0L3,3', parseAll=True)
        self.assertEqual(len(res), 2, 'path should contain two items')

    def test_parse_path_passes_without_elements(self):
        for path in ['', ' ', '\t\n \r\n']:
            with self.subTest(path=path):
                res = g.parseString(path, parseAll=True)
                self.assertEqual(len(res), 0, 'should find no elements in path')

    def test_parse_command_arc_single(self):
        move, arc = g.parseString('M0,0A1,2 3 0 1 10,20', parseAll=True)
        self.assertEqual(arc['type'], 'arcto', 'should get correct type for an arc command')
        self.assertTrue(arc['absolute'], 'should get absolute arc')
        self.assertEqual(len(arc['segments']), 1, 'should get a single segment')
        segment = arc['segments'][0]
        self.assertEqual(segment['rx'], 1.0, 'should get x radius 1')
        self.assertEqual(segment['ry'], 2.0, 'should get y radius 2')
        self.assertEqual(segment['x_axis_rotation'], 3, 'should get x axis rotation 3')
        self.assertEqual(segment['large_arc_flag'], False, 'should get small arc')
        self.assertEqual(segment['sweep_flag'], True, 'should get clockwise sweep')
        self.assertEqual(segment['destination'].x, 10, 'should get correct destination point x coordinate')
        self.assertEqual(segment['destination'].y, 20, 'should get correct destination point y coordinate')

    def test_parse_command_arc_multi(self):
        move, arc = g.parseString('M0,0a1,2 3 0 1 10,20 2 4 5 1 0 -1 2.3', parseAll=True)
        self.assertEqual(arc['type'], 'arcto', 'should get correct type for an arc command')
        self.assertFalse(arc['absolute'], 'should get relative arc')
        self.assertEqual(len(arc['segments']), 2, 'should get two segments')
        segment = arc['segments'][0]
        self.assertEqual(segment['rx'], 1.0, 'should get x radius 1')
        self.assertEqual(segment['ry'], 2.0, 'should get y radius 2')
        self.assertEqual(segment['x_axis_rotation'], 3, 'should get x axis rotation 3')
        self.assertEqual(segment['large_arc_flag'], False, 'should get small arc')
        self.assertEqual(segment['sweep_flag'], True, 'should get clockwise sweep')
        self.assertEqual(segment['destination'].x, 10, 'should get correct destination point x coordinate')
        self.assertEqual(segment['destination'].y, 20, 'should get correct destination point y coordinate')
        segment = arc['segments'][1]
        self.assertEqual(segment['rx'], 2.0, 'should get x radius 1')
        self.assertEqual(segment['ry'], 4.0, 'should get y radius 2')
        self.assertEqual(segment['x_axis_rotation'], 5, 'should get x axis rotation 3')
        self.assertEqual(segment['large_arc_flag'], True, 'should get large arc')
        self.assertEqual(segment['sweep_flag'], False, 'should get counterclockwise sweep')
        self.assertEqual(segment['destination'].x, -1, 'should get correct destination point x coordinate')
        self.assertEqual(segment['destination'].y, 2.3, 'should get correct destination point y coordinate')

    def test_smooth_quadratic_curve_single(self):
        move, curve = g.parseString('M0,0T1.1,2.2', parseAll=True)
        self.assertEqual(curve['type'], 'smooth_quadratic_curveto', 'should get correct type for a smooth quadratic curve command')
        self.assertTrue(curve['absolute'], 'should get absolute curve')
        self.assertEqual(len(curve['segments']), 1, 'should get a single segment')
        segment = curve['segments'][0]
        self.assertEqual(segment.x, 1.1, 'should get correct segment point x coordinate')
        self.assertEqual(segment.y, 2.2, 'should get correct segment point y coordinate')

    def test_smooth_quadratic_curve_multi(self):
        move, curve = g.parseString('M0,0t1.1,2.2,-1.1,.2', parseAll=True)
        self.assertEqual(curve['type'], 'smooth_quadratic_curveto', 'should get correct type for a smooth quadratic curve command')
        self.assertFalse(curve['absolute'], 'should get relative curve')
        self.assertEqual(len(curve['segments']), 2, 'should get segments')
        segment = curve['segments'][0]
        self.assertEqual(segment.x, 1.1, 'should get correct segment point x coordinate')
        self.assertEqual(segment.y, 2.2, 'should get correct segment point y coordinate')
        segment = curve['segments'][1]
        self.assertEqual(segment.x, -1.1, 'should get correct segment point x coordinate')
        self.assertEqual(segment.y, 0.2, 'should get correct segment point y coordinate')

    def test_quadratic_curve_single(self):
        move, curve = g.parseString('M0,0Q.1,2.2,-1,-2', parseAll=True)
        self.assertEqual(curve['type'], 'quadratic_curveto', 'should get correct type for a quadratic curve command')
        self.assertTrue(curve['absolute'], 'should get absolute curve')
        self.assertEqual(len(curve['segments']), 1, 'should get a single segment')
        segment = curve['segments'][0]
        control, destination = segment['control'], segment['destination']
        self.assertEqual(control.x, 0.1, 'should get correct control point x coordinate')
        self.assertEqual(control.y, 2.2, 'should get correct control point y coordinate')
        self.assertEqual(destination.x, -1, 'should get correct destination point x coordinate')
        self.assertEqual(destination.y, -2, 'should get correct destination point y coordinate')

    def test_quadratic_curve_multi(self):
        move, curve = g.parseString('M0,0q.1,2.2,-1,-2 4 5 -7 -1e3', parseAll=True)
        self.assertEqual(curve['type'], 'quadratic_curveto', 'should get correct type for a quadratic curve command')
        self.assertFalse(curve['absolute'], 'should get relative curve')
        self.assertEqual(len(curve['segments']), 2, 'should get two segments')
        segment = curve['segments'][0]
        control, destination = segment['control'], segment['destination']
        self.assertEqual(control.x, 0.1, 'should get correct control point x coordinate')
        self.assertEqual(control.y, 2.2, 'should get correct control point y coordinate')
        self.assertEqual(destination.x, -1, 'should get correct destination point x coordinate')
        self.assertEqual(destination.y, -2, 'should get correct destination point y coordinate')
        segment = curve['segments'][1]
        control, destination = segment['control'], segment['destination']
        self.assertEqual(control.x, 4, 'should get correct control point x coordinate')
        self.assertEqual(control.y, 5, 'should get correct control point y coordinate')
        self.assertEqual(destination.x, -7, 'should get correct destination point x coordinate')
        self.assertEqual(destination.y, -1000, 'should get correct destination point y coordinate')

    def test_smooth_curve_single(self):
        move, curve = g.parseString('M0,0S.1,2.2,-1,-2', parseAll=True)
        self.assertEqual(curve['type'], 'smooth_curveto', 'should get correct type for a smooth curve command')
        self.assertTrue(curve['absolute'], 'should get absolute curve')
        self.assertEqual(len(curve['segments']), 1, 'should get a single segment')
        segment = curve['segments'][0]
        control, destination = segment['control'], segment['destination']
        self.assertEqual(control.x, 0.1, 'should get correct control point x coordinate')
        self.assertEqual(control.y, 2.2, 'should get correct control point y coordinate')
        self.assertEqual(destination.x, -1, 'should get correct destination point x coordinate')
        self.assertEqual(destination.y, -2, 'should get correct destination point y coordinate')

    def test_smooth_curve_multi(self):
        move, curve = g.parseString('M0,0s.1,2.2,-1,-2 4 5 -7 -1e3', parseAll=True)
        self.assertEqual(curve['type'], 'smooth_curveto', 'should get correct type for a smooth curve command')
        self.assertFalse(curve['absolute'], 'should get relative curve')
        self.assertEqual(len(curve['segments']), 2, 'should get two segments')
        segment = curve['segments'][0]
        control, destination = segment['control'], segment['destination']
        self.assertEqual(control.x, 0.1, 'should get correct control point x coordinate')
        self.assertEqual(control.y, 2.2, 'should get correct control point y coordinate')
        self.assertEqual(destination.x, -1, 'should get correct destination point x coordinate')
        self.assertEqual(destination.y, -2, 'should get correct destination point y coordinate')
        segment = curve['segments'][1]
        control, destination = segment['control'], segment['destination']
        self.assertEqual(control.x, 4, 'should get correct control point x coordinate')
        self.assertEqual(control.y, 5, 'should get correct control point y coordinate')
        self.assertEqual(destination.x, -7, 'should get correct destination point x coordinate')
        self.assertEqual(destination.y, -1000, 'should get correct destination point y coordinate')

    def test_curve_single(self):
        move, curve = g.parseString('M0,0C.1,2.2,-1,-2,1e-1,5.5e+1', parseAll=True)
        self.assertEqual(curve['type'], 'curveto', 'should get correct type for a curve command')
        self.assertTrue(curve['absolute'], 'should get absolute curve')
        self.assertEqual(len(curve['segments']), 1, 'should get a single segment')
        segment = curve['segments'][0]
        control1, control2, destination = segment['control1'], segment['control2'], segment['destination']
        self.assertEqual(control1.x, 0.1, 'should get correct control point 1 x coordinate')
        self.assertEqual(control1.y, 2.2, 'should get correct control point 1 y coordinate')
        self.assertEqual(control2.x, -1, 'should get correct control point 2 x coordinate')
        self.assertEqual(control2.y, -2, 'should get correct control point 2 y coordinate')
        self.assertEqual(destination.x, 0.1, 'should get correct destination point x coordinate')
        self.assertEqual(destination.y, 55, 'should get correct destination point y coordinate')

    def test_curve_multi(self):
        move, curve = g.parseString('M0,0c.1,2.2,-1,-2,1e-1,5.5e+1 4 5 -7 -1e3 +12 -5.5e-1', parseAll=True)
        self.assertEqual(curve['type'], 'curveto', 'should get correct type for a curve command')
        self.assertFalse(curve['absolute'], 'should get relative curve')
        self.assertEqual(len(curve['segments']), 2, 'should get two segments')
        segment = curve['segments'][0]
        control1, control2, destination = segment['control1'], segment['control2'], segment['destination']
        self.assertEqual(control1.x, 0.1, 'should get correct control point 1 x coordinate')
        self.assertEqual(control1.y, 2.2, 'should get correct control point 1 y coordinate')
        self.assertEqual(control2.x, -1, 'should get correct control point 2 x coordinate')
        self.assertEqual(control2.y, -2, 'should get correct control point 2 y coordinate')
        self.assertEqual(destination.x, 0.1, 'should get correct destination point x coordinate')
        self.assertEqual(destination.y, 55, 'should get correct destination point y coordinate')
        segment = curve['segments'][1]
        control1, control2, destination = segment['control1'], segment['control2'], segment['destination']
        self.assertEqual(control1.x, 4, 'should get correct control point 1 x coordinate')
        self.assertEqual(control1.y, 5, 'should get correct control point 1 y coordinate')
        self.assertEqual(control2.x, -7, 'should get correct control point 2 x coordinate')
        self.assertEqual(control2.y, -1000, 'should get correct control point 2 y coordinate')
        self.assertEqual(destination.x, 12, 'should get correct destination point x coordinate')
        self.assertEqual(destination.y, -0.55, 'should get correct destination point y coordinate')

    def test_vertical_single(self):
        move, vert = g.parseString('M0,0V10.23', parseAll=True)
        self.assertEqual(vert['type'], 'vertical_lineto', 'should get correct type for a vertical line command')
        self.assertTrue(vert['absolute'], 'should get absolute line')
        self.assertEqual(len(vert['segments']), 1, 'should get a single segment')
        segment = vert['segments'][0]
        self.assertEqual(segment, 10.23, 'should get correct segment y coordinate')

    def test_vertical_multi(self):
        move, vert = g.parseString('M0,0v10.23 -5', parseAll=True)
        self.assertEqual(vert['type'], 'vertical_lineto', 'should get correct type for a vertical line command')
        self.assertFalse(vert['absolute'], 'should get relative line')
        self.assertEqual(len(vert['segments']), 2, 'should get two segments')
        segment = vert['segments'][0]
        self.assertEqual(segment, 10.23, 'should get correct segment y coordinate')
        segment = vert['segments'][1]
        self.assertEqual(segment, -5, 'should get correct segment y coordinate')

    def test_horizontal_single(self):
        move, horiz = g.parseString('M0,0H10.23', parseAll=True)
        self.assertEqual(horiz['type'], 'horizontal_lineto', 'should get correct type for a horizontal line command')
        self.assertTrue(horiz['absolute'], 'should get absolute line')
        self.assertEqual(len(horiz['segments']), 1, 'should get a single segment')
        segment = horiz['segments'][0]
        self.assertEqual(segment, 10.23, 'should get correct segment x coordinate')

    def test_horizontal_multi(self):
        move, horiz = g.parseString('M0,0h10.23 -5', parseAll=True)
        self.assertEqual(horiz['type'], 'horizontal_lineto', 'should get correct type for a horizontal line command')
        self.assertFalse(horiz['absolute'], 'should get relative line')
        self.assertEqual(len(horiz['segments']), 2, 'should get two segments')
        segment = horiz['segments'][0]
        self.assertEqual(segment, 10.23, 'should get correct segment x coordinate')
        segment = horiz['segments'][1]
        self.assertEqual(segment, -5, 'should get correct segment x coordinate')

    def test_line_single(self):
        move, line = g.parseString('M0,0L10.23,-5', parseAll=True)
        self.assertEqual(line['type'], 'lineto', 'should get correct type for a line command')
        self.assertTrue(line['absolute'], 'should get absolute line')
        self.assertEqual(len(line['segments']), 1, 'should get a single segment')
        segment = line['segments'][0]
        self.assertEqual(segment.x, 10.23, 'should get correct segment x coordinate')
        self.assertEqual(segment.y, -5, 'should get correct segment y coordinate')

    def test_line_multi(self):
        move, line = g.parseString('M0,0l10.23,-5 3 -2.3e-1', parseAll=True)
        self.assertEqual(line['type'], 'lineto', 'should get correct type for a line command')
        self.assertFalse(line['absolute'], 'should get relative line')
        self.assertEqual(len(line['segments']), 2, 'should get two segments')
        segment = line['segments'][0]
        self.assertEqual(segment.x, 10.23, 'should get correct segment x coordinate')
        self.assertEqual(segment.y, -5, 'should get correct segment y coordinate')
        segment = line['segments'][1]
        self.assertEqual(segment.x, 3, 'should get correct segment x coordinate')
        self.assertEqual(segment.y, -0.23, 'should get correct segment y coordinate')

    def test_closepath(self):
        move, close = g.parseString('M0,0Z', parseAll=True)
        self.assertEqual(close['type'], 'closepath', 'should get correct type for a closepath command')
        move, close = g.parseString('m 1 2 z', parseAll=True)
        self.assertEqual(close['type'], 'closepath', 'should get correct type for a closepath command')

    def test_move_single(self):
        (move,) = g.parseString('M2.,-.3', parseAll=True)
        self.assertEqual(move['type'], 'moveto', 'should get correct type for a moveto command')
        self.assertTrue(move['absolute'], 'should get absolute move')
        self.assertEqual(len(move['segments']), 1, 'should get a single segment')
        segment = move['segments'][0]
        self.assertEqual(segment.x, 2, 'should get correct move x coordinate')
        self.assertEqual(segment.y, -0.3, 'should get correct move y coordinate')

    def test_move_multi(self):
        (move,) = g.parseString('m2.,-.3-2-3', parseAll=True)
        self.assertEqual(move['type'], 'moveto', 'should get correct type for a moveto command')
        self.assertFalse(move['absolute'], 'should get relative move')
        self.assertEqual(len(move['segments']), 2, 'should get two segments')
        segment = move['segments'][0]
        self.assertEqual(segment.x, 2, 'should get correct move x coordinate')
        self.assertEqual(segment.y, -0.3, 'should get correct move y coordinate')
        segment = move['segments'][1]
        self.assertEqual(segment.x, -2, 'should get correct move x coordinate')
        self.assertEqual(segment.y, -3, 'should get correct move y coordinate')
