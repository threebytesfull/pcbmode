import unittest
from unittest.mock import patch

import pcbmode.config
from pcbmode.config import Config

class TestConfig(unittest.TestCase):
    """Test config dictionary"""

    def setUp(self):
        self.top_level_keys = 'cfg brd stl pth msg stk rte tmp'.split()

    def test_config_dict_entries(self):
        expected_keys = 'cfg brd stl pth msg stk'.split()
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertTrue(hasattr(pcbmode.config, key), 'config should contain {} dict'.format(key))

    def test_config_class_properties(self):
        c = Config()
        for prop in self.top_level_keys:
            attr_dict = getattr(c, prop, None)
            self.assertIsNotNone(attr_dict, 'Config class should have {} property'.format(prop))

    def test_config_properties_are_same_as_globals(self):
        c = Config()
        c.tmp['test'] = 'data'
        self.assertEqual(pcbmode.config.tmp.get('test'), 'data', 'object attribute and global should be same dict')

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
        c = Config()
        with self.assertRaises(KeyError, msg='should raise KeyError when no top-level key supplied to get()'):
            c.get()

    def test_config_get_with_nonexistent_top_level_key(self):
        c = Config()
        with self.assertRaises(KeyError, msg='should raise KeyError when nonexistent top-level key supplied to get()'):
            c.get('no_such_key')

    def test_config_get_with_top_level_only(self):
        c = Config()
        for top in self.top_level_keys:
            dict_from_attr = getattr(c, top)
            dict_from_get = c.get(top)
            self.assertIs(dict_from_get, dict_from_attr, 'top-level get should return same object as attribute')

    def test_config_get_with_two_levels(self):
        c = Config()
        for top in self.top_level_keys:
            dict_from_attr = getattr(c, top)
            dict_from_attr['example_key'] = '{}_value'.format(top)
            value = c.get(top, 'example_key')
            self.assertEqual(value, '{}_value'.format(top), 'should get expected value from two-level config get()')

    def test_config_get_with_three_levels(self):
        c = Config()
        for top in self.top_level_keys:
            dict_from_attr = getattr(c, top)
            dict_from_attr['second'] = { 'third': 'value_for_{}'.format(top) }
            self.assertEqual(c.get(top, 'second', 'third'), 'value_for_{}'.format(top), 'should get expected value from three-level config get()')
            self.assertEqual(c.get(top, 'second', 'nonexistent'), None, 'should get None from nonexistent dict item')

    def test_config_get_with_array(self):
        c = Config()
        for top in self.top_level_keys:
            dict_from_attr = getattr(c, top)
            dict_from_attr['food'] = [ { 'fruit': 'apple' }, { 'fruit': 'banana' } ]
            self.assertEqual(c.get(top, 'food', 0, 'fruit'), 'apple', 'should get expected value from first item in array')
            self.assertEqual(c.get(top, 'food', 1, 'fruit'), 'banana', 'should get expected value from second item in array')
            self.assertEqual(c.get(top, 'food', 2, 'fruit'), None, 'should get None from nonexistent array item')
