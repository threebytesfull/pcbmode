from unittest import TestCase
from unittest.mock import Mock, patch, mock_open

from pcbmode.utils import utils
from pcbmode.utils.point import Point

class TestUtils(TestCase):
    """Test utils class"""

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

    # dictFromJsonFile tests
    def test_dict_from_good_json_file(self):
        json_src = '{"top":{"val1":1,"val2":2}}'
        with patch('tests.test_utils.utils.open', mock_open(read_data=json_src)) as m:
            json_data = utils.dictFromJsonFile('file.json')
        m.assert_called_once_with('file.json', 'r')
        self.assertEqual(json_data, {'top': { 'val1': 1, 'val2': 2 }}, 'should get expected data from JSON')

    def test_dict_from_json_file_with_duplicate_keys(self):
        json_src = '{"top":{"val1":1,"val1":2}}'
        with patch('tests.test_utils.utils.msg.error') as e:
            with patch('tests.test_utils.utils.open', mock_open(read_data=json_src)) as m:
                json_data = utils.dictFromJsonFile('file.json')
            e.assert_called_with("duplicate key ('val1') specified in file.json", KeyError)

    def test_dict_from_json_file_with_duplicate_keys_info_only(self):
        json_src = '{"top":{"val1":1,"val1":2}}'
        with patch('tests.test_utils.utils.msg.error') as e:
            with patch('tests.test_utils.utils.open', mock_open(read_data=json_src)) as m:
                json_data = utils.dictFromJsonFile('file.json', False)
            e.assert_called_with("duplicate key ('val1') specified in file.json", KeyError)

    def test_dict_from_nonexistent_json_file(self):
        with patch('tests.test_utils.utils.open', mock_open()) as m:
            m.side_effect = IOError()
            with patch('tests.test_utils.utils.msg.error') as e:
                e.side_effect = Exception()
                with self.assertRaises(Exception):
                    json_data = utils.dictFromJsonFile('nonexistent.json')
            e.assert_called_with("Couldn't open JSON file: nonexistent.json", IOError)

    def test_dict_from_nonexistent_json_file_info_only(self):
        with patch('tests.test_utils.utils.open', mock_open()) as m:
            m.side_effect = IOError()
            with patch('tests.test_utils.utils.msg.info') as e:
                e.side_effect = Exception()
                with self.assertRaises(Exception):
                    json_data = utils.dictFromJsonFile('nonexistent.json', False)
            e.assert_called_with("Couldn't open JSON file: nonexistent.json", IOError)

    # getLayerList tests
    def test_getLayerList(self):
        pass

    # def getSurfaceLayers tests
    def test_getSurfaceLayers(self):
        pass

    # getInternalLayers tests
    def test_getInternalLayers(self):
        pass

    # getExtendedLayerList tests
    def test_getExtendedLayerList(self):
        pass

    # getExtendedSheetList tests
    def test_getExtendedSheetList(self):
        pass

    # create_dir tests
    def test_create_dir(self):
        pass

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

    # interpret_svg_matrix tests
    def test_interpret_svg_matrix(self):
        pass

    # parseRefDef tests
    def test_parseRefDef(self):
        pass

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
        pass

    # getStyleAttrib tests
    def test_getStyleAttrib(self):
        pass

    # niceFloat tests
    def test_niceFloat(self):
        pass

    # parseTransform tests
    def test_parseTransform(self):
        pass

    # parseSvgMatrix tests
    def test_parseSvgMatrix(self):
        pass
