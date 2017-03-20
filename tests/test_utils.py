try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import Mock, patch, mock_open
except ImportError:
    from mock import Mock, patch, mock_open

from pcbmode.utils import utils
from pcbmode.utils.point import Point
from pcbmode.config import Config

class TestUtils(unittest.TestCase):
    """Test utils class"""

    def setUp(self):
        self.c = Config(clean=True)

    # dictToStyleText tests
    def test_style_string_from_empty_dictionary(self):
        style = utils.dictToStyleText({})
        self.assertEqual(style, '', 'should get empty style string from empty style dictionary')

    def test_style_string_from_dictionary_with_single_item(self):
        style = utils.dictToStyleText({ 'font-size': 12 })
        self.assertEqual(style, 'font-size:12;', 'should get correct style string from single-item dictionary')

    # openBoardSVG tests
    def test_openBoardSVG(self):
        pass

    # parseDimension tests
    def test_parse_valid_dimension(self):
        test_cases = [
            ('1.1', (1.1, None)),
            ('-1.1', (-1.1, None)),
            ('10 mm', (10, 'mm')),
            ('-3in', (-3, 'in')),
            ('0', (0, None)),
        ]
        for input_string, expected_output in test_cases:
            with self.subTest(input_string=input_string):
                output = utils.parseDimension(input_string)
                self.assertEqual(output, expected_output, 'should get expected dimension result')

    def test_parse_no_dimension(self):
        self.assertEqual(utils.parseDimension(None), (None, None), 'should not get dimension without string')

    def test_parse_invalid_dimension(self):
        test_cases = [
            'invalid',
            '',
        ]
        for input_string in test_cases:
            with self.subTest(input_string=input_string):
                with self.assertRaises(AttributeError):
                    utils.parseDimension(input_string)

    # to_Point tests
    def test_to_Point_with_no_arguments(self):
        p = utils.to_Point()
        self.assertEqual(p.x, 0, 'default x coord should be 0')
        self.assertEqual(p.y, 0, 'default y coord should be 0')
        self.assertIsInstance(p, Point)

    def test_to_Point_with_list(self):
        p = utils.to_Point([3, 5])
        self.assertEqual(p.x, 3, 'should store positive x coord')
        self.assertEqual(p.y, 5, 'should store negative y coord')
        self.assertIsInstance(p, Point)

        p = utils.to_Point([-1, -4])
        self.assertEqual(p.x, -1, 'should store negative x coord')
        self.assertEqual(p.y, -4, 'should store negative y coord')
        self.assertIsInstance(p, Point)

        p = utils.to_Point([1.3, -0.5])
        self.assertEqual(p.x, 1.3, 'should store floating point x coord')
        self.assertEqual(p.y, -0.5, 'should store floating point y coord')
        self.assertIsInstance(p, Point)

    # toPoint tests
    def test_toPoint_with_no_arguments(self):
        p = utils.toPoint()
        self.assertEqual(p.x, 0, 'default x coord should be 0')
        self.assertEqual(p.y, 0, 'default y coord should be 0')
        self.assertIsInstance(p, Point)

    def test_toPoint_with_none(self):
        p = utils.toPoint(None)
        self.assertIsNone(p, 'should not get a Point for coords None')

    def test_toPoint_with_list(self):
        p = utils.toPoint([3, 5])
        self.assertEqual(p.x, 3, 'should store positive x coord')
        self.assertEqual(p.y, 5, 'should store negative y coord')
        self.assertIsInstance(p, Point)

        p = utils.toPoint([-1, -4])
        self.assertEqual(p.x, -1, 'should store negative x coord')
        self.assertEqual(p.y, -4, 'should store negative y coord')
        self.assertIsInstance(p, Point)

        p = utils.toPoint([1.3, -0.5])
        self.assertEqual(p.x, 1.3, 'should store floating point x coord')
        self.assertEqual(p.y, -0.5, 'should store floating point y coord')
        self.assertIsInstance(p, Point)
        pass

    # get_git_revision tests
    def test_get_git_revision(self):
        with patch('tests.test_utils.utils.get_distribution') as mock_get_distribution:
            mock_distribution = Mock()
            mock_distribution.version = '0.0.1dev1'

            mock_get_distribution.return_value = mock_distribution

            ver = utils.get_git_revision()
            self.assertTrue(mock_get_distribution.called, 'should call get_distribution')
            args, kwargs = mock_get_distribution.call_args
            self.assertEqual(args[0], ('pcbmode'), 'should specify pcbmode package')
            self.assertEqual(ver, '0.0.1dev1', 'should use version from distribution')

    # makePngs tests
    def test_makePngs(self):
        pass

    # getLayerList tests
    def test_getLayerList_returns_2_layer_signal_layers(self):
        self.c.load_defaults()
        layer_list, layer_names = utils.getLayerList()
        self.assertEqual(len(layer_list), 2, 'should get details of two signal layers')
        self.assertEqual(layer_names, 'top bottom'.split(), 'should get two expected signal layers')
        self.assertEqual([layer['name'] for layer in layer_list], layer_names, 'names from layer list should match layer names returned')

    @patch('pcbmode.config.Config._default_stackup_name', 'four-layer')
    def test_getLayerList_returns_4_layer_signal_layers(self):
        self.c.load_defaults()
        layer_list, layer_names = utils.getLayerList()
        self.assertEqual(len(layer_list), 4, 'should get details of four signal layers')
        self.assertEqual(layer_names, 'top internal-1 internal-2 bottom'.split(), 'should get four expected signal layers')
        self.assertEqual([layer['name'] for layer in layer_list], layer_names, 'names from layer list should match layer names returned')

    # def getSurfaceLayers tests
    def test_getSurfaceLayers_returns_layers_of_2(self):
        self.c.load_defaults()
        surface_layers = utils.getSurfaceLayers()
        self.assertEqual(len(surface_layers), 2, 'should get details of two surface layers')
        self.assertEqual(surface_layers, 'top bottom'.split(), 'names from layer list should match layer names returned')

    @patch('pcbmode.config.Config._default_stackup_name', 'four-layer')
    def test_getSurfaceLayers_returns_outer_layers_of_4(self):
        self.c.load_defaults()
        surface_layers = utils.getSurfaceLayers()
        self.assertEqual(len(surface_layers), 2, 'should get details of two surface layers')
        self.assertEqual(surface_layers, 'top bottom'.split(), 'names from layer list should match layer names returned')

    # getInternalLayers tests
    def test_getInternalLayers_of_2(self):
        self.c.load_defaults()
        internal_layers = utils.getInternalLayers()
        self.assertEqual(len(internal_layers), 0, 'should get details of no internal layers')

    @patch('pcbmode.config.Config._default_stackup_name', 'four-layer')
    def test_getInternalLayers_of_4(self):
        self.c.load_defaults()
        internal_layers = utils.getInternalLayers()
        self.assertEqual(len(internal_layers), 2, 'should get details of two internal layers')
        self.assertEqual(internal_layers, 'internal-1 internal-2'.split(), 'names from layer list should match layer names returned')

    # getExtendedLayerList tests
    def test_getExtendedLayerList_2_layer(self):
        self.c.load_defaults()
        layers = utils.getExtendedLayerList('top bottom'.split())
        self.assertEqual(layers, 'top bottom'.split(), 'should not add internal layers when internal not specified')
        layers = utils.getExtendedLayerList('top internal bottom'.split())
        self.assertEqual(layers, 'top bottom'.split(), 'should not add internal layers in a 2-layer board')

    @patch('pcbmode.config.Config._default_stackup_name', 'four-layer')
    def test_getExtendedLayerList_4_layer(self):
        self.c.load_defaults()
        layers = utils.getExtendedLayerList('top bottom'.split())
        self.assertEqual(layers, 'top bottom'.split(), 'should not add internal layers when internal not specified')
        layers = utils.getExtendedLayerList('top internal bottom'.split())
        self.assertEqual(layers, 'top bottom internal-1 internal-2'.split(), 'should expand internal layers in a 4-layer board')

    # getExtendedSheetList tests
    def test_getExtendedSheetList(self):
        pass

    # create_dir tests
    @patch('os.makedirs')
    def test_create_dir_not_already_present(self, fake_makedirs):
        utils.create_dir('dummy')
        fake_makedirs.assert_called_with('dummy')

    @patch('os.makedirs')
    @patch('os.path.isdir')
    def test_create_dir_already_present(self, fake_isdir, fake_makedirs):
        fake_makedirs.side_effect = FileExistsError()
        fake_isdir.return_value = True
        utils.create_dir('dummy')
        fake_makedirs.assert_called_with('dummy')
        fake_isdir.assert_called_with('dummy')

    @patch('os.makedirs')
    @patch('os.path.isdir')
    @patch('builtins.print')
    def test_create_dir_failure(self, fake_print, fake_isdir, fake_makedirs):
        fake_makedirs.side_effect = FileExistsError()
        fake_isdir.return_value = False
        with self.assertRaises(FileExistsError):
            utils.create_dir('dummy')
        fake_makedirs.assert_called_with('dummy')
        fake_isdir.assert_called_with('dummy')

    # add_dict_values tests
    def test_add_dict_values(self):
        d1 = {'apple': 3, 'banana': 7, 'pear': -2}
        d2 = {'banana': 8, 'pear': 12, 'orange': 0.3}
        result = utils.add_dict_values(d1, d2)
        self.assertEqual(result, {'apple':3, 'banana':15, 'pear':10, 'orange':0.3}, 'should add dicts correctly')

    # process_meander_type tests
    def test_process_meander_type(self):
        pass

    # checkForPoursInLayer tests
    def test_checkForPoursInLayer(self):
        pass

    # parserefdef tests
    def test_parse_invalid_refdef(self):
        test_cases = [
            '',
            'NotAGoodRefDef',
            '99',
            'X',
            '1R',
        ]
        for refdef in test_cases:
            with self.subTest(refdef=refdef):
                self.assertEqual(utils.parse_refdef(refdef), (None, None, None), 'should not parse invalid refdef')

    def test_parse_valid_refdef(self):
        test_cases = [
            ('R1', ('R', 1, None)),
            ('CON2', ('CON', 2, None)),
            ('J1234', ('J', 1234, None)),
            ('IC1-A', ('IC', 1, '-A')),
            ('U3 B', ('U', 3, ' B')),
            ('Unlikely1', ('Unlikely', 1, None)),
            ('Bad[data1', ('Bad[data', 1, None)), # FIXME: bug? A-z should be A-Z
            ('Bug?..%%1', ('Bug?..%%', 1, None)), # FIXME: bug? \D in category
        ]
        for refdef, expected_output in test_cases:
            with self.subTest(refdef=refdef):
                self.assertEqual(utils.parse_refdef(refdef), expected_output, 'should parse valid refdef')

    # renumberRefDefs tests
    def test_renumberRefDefs(self):
        pass

    # getTextParams tests
    def test_getTextParams(self):
        pass

    # textToPath tests
    def test_textToPath(self):
        pass

    # digest tests
    def test_digest(self):
        input_string = 'PCBmodE'
        output_hash = '2dc7e7def877f609c8532c01a2a357ae'
        for num_chars in range(1, 33):
            with self.subTest(num_chars=num_chars):
                self.c.cfg['digest-digits'] = num_chars
                output = utils.digest(input_string)
                # FIXME: this is probably a bug - the length is always one less than the configured digest-digits
                self.assertEqual(output, output_hash[:num_chars-1], 'should get correct {} character digest hash'.format(num_chars))

    # getStyleAttrib tests
    def test_getStyleAttrib(self):
        test_cases = [
            ('one:1; two:2',
                {
                    'one': '1',
                    'two': '2',
                    'three': None,
                }
            ),
            ('  fill:#000;stroke:#000; stroke-linejoin: round;stroke-width:0.9;stroke-linecap:round;',
                {
                    'fill': '#000',
                    'stroke': '#000',
                    'stroke-linejoin': 'round',
                    'stroke-width': '0.9',
                    'stroke-linecap': 'round',
                }
            ),
        ]
        for input_string, expected_values in test_cases:
            with self.subTest(input_string=input_string):
                for attrib, expected_value in expected_values.items():
                    with self.subTest(attrib=attrib):
                        value = utils.getStyleAttrib(input_string, attrib)
                        self.assertEqual(value, expected_value, 'should get correct {} attribute from {}'.format(attrib, input_string))

    # niceFloat tests
    def test_niceFloat(self):
        test_cases = [
            (1.0, 1.0),
            (1.01, 1.01),
            (1.001, 1.001),
            (1.0001, 1.0001),
            (1.00001, 1.00001),
            (1.000001, 1.000001),
            (1.0000001, 1.0),
            (-1.0, -1.0),
            (-1.01, -1.01),
            (-1.001, -1.001),
            (-1.0001, -1.0001),
            (-1.00001, -1.00001),
            (-1.000001, -1.000001),
            (-1.0000001, -1.0),
        ]
        for input_num, expected_output in test_cases:
            with self.subTest(input_num=input_num):
                output = utils.niceFloat(input_num)
                self.assertEqual(output, expected_output, 'should format {} correctly'.format(input_num))

    # parseTransform tests
    def test_parse_bad_transform(self):
        with self.assertRaises(Exception):
            with patch('tests.test_utils.utils.msg.error') as e:
                e.side_effect = Exception()
                utils.parseTransform('unknown(99)')

    def test_parse_good_transform(self):
        test_cases = [
            (None, {'type':'translate', 'location':Point()}),
            ('translate(0,0)', {'type':'translate', 'location':Point()}),
            (' translate( 0.5, +70)', {'type':'translate', 'location':Point(0.5,70)}),
            ('translate (-30,1.5e3 )', {'type':'translate', 'location':Point(-30,1.5e3)}),
            ('translate(+1.06e-3,0.9) ', {'type':'translate', 'location':Point(1.06e-3,0.9)}),
            ('matrix(0,1,-1,0,0,0)', {'type':'matrix', 'location':Point(0,0), 'rotate':0, 'scale':1}),
            ('  matrix(0.4,0,0,0.4,4,0)', {'type':'matrix', 'location':Point(4,0), 'rotate':0, 'scale':0.4}),
            ('matrix(0.8,0,0,0.8,10,0) ', {'type':'matrix', 'location':Point(10, 0), 'rotate':0, 'scale':0.8}),
            ('matrix(0.28222222,0,0,0.28222224,-48.3,-8.3146356)', {'type':'matrix', 'location':Point(-48.3,-8.3146356), 'rotate':0, 'scale':0.28222224}),
            ('matrix(-1.1860592,0,0,1.1860592,-88.663335,-57.031569)', {'type':'matrix', 'location':Point(-88.663335,-57.031569), 'rotate':0, 'scale':1.1860592}),
            ('matrix(0.86602540,0.5,-0.5,0.86602540,5,3.5)', {'type':'matrix', 'location':Point(5,3.5), 'rotate':30.0, 'scale':1}), # 30deg ccw - shouldn't this be -30 in pcbmode?
        ]
        for transform, expected_output in test_cases:
            with self.subTest(transform=transform):
                data = utils.parseTransform(transform)
                for key,val in expected_output.items():
                    with self.subTest(key=key, val=val):
                        self.assertAlmostEqual(data.get(key), val, msg='should get correct {} from transform {}'.format(key, transform), delta=1e-6)

    # parseSvgMatrix tests
    def test_parseSvgMatrix(self):
        test_cases = [
            ('matrix(0,1,-1,0,0,0)', (Point(0,0), 0, 1)),
            ('  matrix(0.4,0,0,0.4,4,0)', (Point(4,0), 0, 0.4)),
            ('matrix(0.8,0,0,0.8,10,0) ', (Point(10, 0), 0, 0.8)),
            ('matrix(0.28222222,0,0,0.28222224,-48.3,-8.3146356)', (Point(-48.3,-8.3146356), 0, 0.28222224)),
            ('matrix(-1.1860592,0,0,1.1860592,-88.663335,-57.031569)', (Point(-88.663335,-57.031569), 0, 1.1860592)),
            ('matrix(0.86602540,0.5,-0.5,0.86602540,5,3.5)', (Point(5,3.5), 30.0, 1)), # 30deg ccw - shouldn't this be -30 in pcbmode?
        ]
        for matrix, expected_output in test_cases:
            with self.subTest(matrix=matrix):
                coord, angle, scale = utils.parseSvgMatrix(matrix)
                self.assertAlmostEqual(coord.x, expected_output[0].x, msg='should get correct x coord from SVG matrix')
                self.assertAlmostEqual(coord.y, expected_output[0].y, msg='should get correct y coord from SVG matrix')
                self.assertAlmostEqual(angle, expected_output[1], msg='should get correct angle from SVG matrix', delta=1e-6)
                self.assertAlmostEqual(scale, expected_output[2], msg='should get correct scale from SVG matrix')
