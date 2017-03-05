from unittest import TestCase
from unittest.mock import patch, mock_open

import pcbmode.utils.json

class TestJson(TestCase):
    """Test pcbmode.utils.json"""

    # dictFromJsonFile tests
    def test_dict_from_good_json_file(self):
        json_src = '{"top":{"val1":1,"val2":2}}'
        with patch('pcbmode.utils.json.open', mock_open(read_data=json_src)) as m:
            json_data = pcbmode.utils.json.dictFromJsonFile('file.json')
        m.assert_called_once_with('file.json', 'r')
        self.assertEqual(json_data, {'top': { 'val1': 1, 'val2': 2 }}, 'should get expected data from JSON')

    def test_dict_from_json_file_with_duplicate_keys(self):
        json_src = '{"top":{"val1":1,"val1":2}}'
        with patch('pcbmode.utils.json.msg.error') as e:
            with patch('pcbmode.utils.json.open', mock_open(read_data=json_src)) as m:
                json_data = pcbmode.utils.json.dictFromJsonFile('file.json')
            e.assert_called_with("duplicate key ('val1') specified in file.json", KeyError)

    def test_dict_from_json_file_with_duplicate_keys_info_only(self):
        json_src = '{"top":{"val1":1,"val1":2}}'
        with patch('pcbmode.utils.json.msg.error') as e:
            with patch('pcbmode.utils.json.open', mock_open(read_data=json_src)) as m:
                json_data = pcbmode.utils.json.dictFromJsonFile('file.json', False)
            e.assert_called_with("duplicate key ('val1') specified in file.json", KeyError)

    def test_dict_from_nonexistent_json_file(self):
        with patch('pcbmode.utils.json.open', mock_open()) as m:
            m.side_effect = IOError()
            with patch('pcbmode.utils.json.msg.error') as e:
                e.side_effect = Exception()
                with self.assertRaises(Exception):
                    json_data = pcbmode.utils.json.dictFromJsonFile('nonexistent.json')
            e.assert_called_with("Couldn't open JSON file: nonexistent.json", IOError)

    def test_dict_from_nonexistent_json_file_info_only(self):
        with patch('pcbmode.utils.json.open', mock_open()) as m:
            m.side_effect = IOError()
            with patch('pcbmode.utils.json.msg.info') as e:
                e.side_effect = Exception()
                with self.assertRaises(Exception):
                    json_data = pcbmode.utils.json.dictFromJsonFile('nonexistent.json', False)
            e.assert_called_with("Couldn't open JSON file: nonexistent.json", IOError)

