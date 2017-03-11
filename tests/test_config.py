import unittest
from unittest.mock import patch

import os
import pkg_resources

import pcbmode.config
from pcbmode.config import Config

class TestConfig(unittest.TestCase):
    """Test config dictionary"""

    def setUp(self):
        self.top_level_keys = 'cfg brd stl pth msg stk rte tmp'.split()
        self.c = Config(clean=True)

    def test_config_dict_entries(self):
        expected_keys = 'cfg brd stl pth msg stk'.split()
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertTrue(hasattr(pcbmode.config, key), 'config should contain {} dict'.format(key))

    def test_config_class_properties(self):
        for prop in self.top_level_keys:
            attr_dict = getattr(self.c, prop, None)
            self.assertIsNotNone(attr_dict, 'Config class should have {} property'.format(prop))

    def test_config_properties_are_same_as_globals(self):
        self.c.tmp['test'] = 'data'
        self.assertEqual(pcbmode.config.tmp.get('test'), 'data', 'object attribute and global should be same dict')

    def test_config_subscripts_are_same_as_globals(self):
        self.assertIs(self.c.get('cfg'), self.c['cfg'], 'config subscript for {} should be same object as global'.format('cfg'))

    def test_config_init_with_clean(self):
        c1 = Config()
        c1.tmp['test'] = 'data'
        c2 = Config()
        self.assertEqual(c2.tmp['test'], 'data', 'config object should reuse config by default')
        c3 = Config(clean=True)
        with self.assertRaises(KeyError, msg='config object should not reuse config if clean is set'):
            val = c3.tmp['test']
        c4 = Config(clean=True, defaults={'tmp':{'fish': 'salmon'}})
        self.assertEqual(c4.tmp['fish'], 'salmon', 'config object should clean with defaults if supplied')
        c5 = Config()
        self.assertEqual(c5.tmp['fish'], 'salmon', 'config object should retain defaults from earlier instance')

    def test_config_get_with_no_top_level_key(self):
        with self.assertRaises(KeyError, msg='should raise KeyError when no top-level key supplied to get()'):
            self.c.get()

    def test_config_get_with_nonexistent_top_level_key(self):
        with self.assertRaises(KeyError, msg='should raise KeyError when nonexistent top-level key supplied to get()'):
            self.c.get('no_such_key')

    def test_config_get_with_top_level_only(self):
        for top in self.top_level_keys:
            dict_from_attr = getattr(self.c, top)
            dict_from_get = self.c.get(top)
            self.assertIs(dict_from_get, dict_from_attr, 'top-level get should return same object as attribute')

    def test_config_get_with_two_levels(self):
        for top in self.top_level_keys:
            dict_from_attr = getattr(self.c, top)
            dict_from_attr['example_key'] = '{}_value'.format(top)
            value = self.c.get(top, 'example_key')
            self.assertEqual(value, '{}_value'.format(top), 'should get expected value from two-level config get()')

    def test_config_get_with_three_levels(self):
        for top in self.top_level_keys:
            dict_from_attr = getattr(self.c, top)
            dict_from_attr['second'] = { 'third': 'value_for_{}'.format(top) }
            self.assertEqual(self.c.get(top, 'second', 'third'), 'value_for_{}'.format(top), 'should get expected value from three-level config get()')
            self.assertEqual(self.c.get(top, 'second', 'nonexistent'), None, 'should get None from nonexistent dict item')

    def test_config_get_with_array(self):
        for top in self.top_level_keys:
            dict_from_attr = getattr(self.c, top)
            dict_from_attr['food'] = [ { 'fruit': 'apple' }, { 'fruit': 'banana' } ]
            self.assertEqual(self.c.get(top, 'food', 0, 'fruit'), 'apple', 'should get expected value from first item in array')
            self.assertEqual(self.c.get(top, 'food', 1, 'fruit'), 'banana', 'should get expected value from second item in array')
            self.assertEqual(self.c.get(top, 'food', 2, 'fruit'), None, 'should get None from nonexistent array item')

    def test_load_defaults(self):
        for top in self.top_level_keys:
            with self.subTest(key=top):
                self.assertEqual(self.c.get(top), {}, msg="should start with no data for config.{}".format(top))
        self.c.load_defaults()
        for top in self.top_level_keys:
            with self.subTest(key=top):
                self.assertIs(self.c.get(top), vars(pcbmode.config)[top], 'should not break object identity for {}'.format(top))
                self.assertIsInstance(self.c.get(top), dict, 'config.{} should be a dict'.format(top))
        self.assertEqual(self.c.get('cfg', 'refdef-index', 'common', 'AT'), 'Attenuator', 'should read global config file')
        self.assertIsNotNone(self.c.get('stl'), 'style data should be present after load_defaults')
        self.assertIsNotNone(self.c.get('stk'), 'stackup data should be present after load_defaults')

    def test_global_config_path(self):
        self.assertEqual(self.c.global_config_path, pkg_resources.resource_filename('pcbmode', pcbmode.config.DEFAULT_CONFIG_FILENAME), 'should get correct global config path')

    @patch('pcbmode.config.Config._default_config_filename', 'no_such_file.json')
    def test_global_config_path_with_custom_filename(self):
        self.assertEqual(self.c.global_config_path, pkg_resources.resource_filename('pcbmode', 'no_such_file.json'), 'should get correct global config path with custom filename')

    @patch('pcbmode.utils.messages.error')
    @patch('pcbmode.config.Config._default_config_filename', 'no_such_file.json')
    def test_load_defaults_with_missing_global_file(self, e):
        self.c.load_defaults()
        e.assert_called_once()
        self.assertRegex(e.call_args[0][0], r"Couldn't open PCBmodE's configuration file no_such_file\.json")

    @patch('pcbmode.utils.messages.error')
    @patch('pcbmode.config.Config._default_config_filename', 'global_defaults.json')
    def test_load_defaults_with_custom_missing_file(self, e):
        self.c.load_defaults(filename='missing_config_file.json')
        e.assert_called_once()
        message_lines = e.call_args[0][0].split('\n')
        self.assertRegex(message_lines[0], r"Couldn't open PCBmodE's configuration file missing_config_file.json.", 'should get missing config message')
        self.assertRegex(message_lines[1], r"missing_config_file.json", 'should look for specified config file first')
        self.assertRegex(message_lines[2], r"global_defaults.json", 'should fall back to global config file')

    def test_path_in_location_without_base_dir(self):
        self.assertIsNone(self.c.get('cfg', 'base-dir'), 'base-dir should not be set')
        with self.assertRaisesRegex(Exception, r"cannot determine paths until base-dir has been set"):
            self.c.path_in_location('build', 'test.svg')

    def test_path_in_location_with_unknown_location(self):
        self.c.cfg['base-dir'] = os.getcwd()
        self.assertIsNotNone(self.c.get('cfg', 'base-dir'), 'base-dir should be set')
        with self.assertRaisesRegex(Exception, r'cannot determine path for unknown location'):
            self.c.path_in_location('build', 'test.svg')

    def test_path_in_location_with_known_location(self):
        self.c.cfg['base-dir'] = 'some_base_dir'
        self.c.cfg['locations'] = { 'build' : 'some_build_directory' }
        self.assertEqual(self.c.get('cfg', 'base-dir'), 'some_base_dir', 'base-dir should be set')
        self.assertEqual(self.c.get('cfg', 'locations', 'build'), 'some_build_directory', 'locations.build should be set')
        path = self.c.path_in_location('build', 'test.svg')
        self.assertEqual(path, os.path.join('some_base_dir', 'some_build_directory', 'test.svg'), 'should get expected file path')

    def test_path_in_location_with_known_location_absolute(self):
        self.c.cfg['base-dir'] = 'some_base_dir'
        self.c.cfg['locations'] = { 'build': 'some_build_directory' }
        self.assertEqual(self.c.get('cfg', 'base-dir'), 'some_base_dir', 'base-dir should be set')
        self.assertEqual(self.c.get('cfg', 'locations', 'build'), 'some_build_directory', 'locations.build should be set')
        path = self.c.path_in_location('build', 'test.svg', absolute=True)
        self.assertEqual(path, os.path.join(os.getcwd(), 'some_base_dir', 'some_build_directory', 'test.svg'), 'should get expected file path')

    def test_longer_path_in_location_with_known_location(self):
        self.c.cfg['base-dir'] = 'some_base_dir'
        self.c.cfg['locations'] = { 'build' : 'some_build_directory' }
        self.assertEqual(self.c.get('cfg', 'base-dir'), 'some_base_dir', 'base-dir should be set')
        self.assertEqual(self.c.get('cfg', 'locations', 'build'), 'some_build_directory', 'locations.build should be set')
        path = self.c.path_in_location('build', 'some_intermediate_dir', 'another_intermediate_dir', 'test.svg')
        self.assertEqual(path, os.path.join('some_base_dir', 'some_build_directory', 'some_intermediate_dir', 'another_intermediate_dir', 'test.svg'), 'should get expected file path')

    def test_longer_path_in_location_with_known_location_absolute(self):
        self.c.cfg['base-dir'] = 'some_base_dir'
        self.c.cfg['locations'] = { 'build': 'some_build_directory' }
        self.assertEqual(self.c.get('cfg', 'base-dir'), 'some_base_dir', 'base-dir should be set')
        self.assertEqual(self.c.get('cfg', 'locations', 'build'), 'some_build_directory', 'locations.build should be set')
        path = self.c.path_in_location('build', 'some_intermediate_dir', 'another_intermediate_dir', 'test.svg', absolute=True)
        self.assertEqual(path, os.path.join(os.getcwd(), 'some_base_dir', 'some_build_directory', 'some_intermediate_dir', 'another_intermediate_dir', 'test.svg'), 'should get expected file path')
