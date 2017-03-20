try:
    import unittest2 as unittest
except ImportError:
    import unittest

from tests.example_data import ExampleData

class TestExampleData(unittest.TestCase):
    """Test ExampleData class"""

    def test_instantiate_with_valid_single_level_path(self):
        d = ExampleData('simple.txt')
        self.assertIsNotNone(d, 'should get an example data object')
        self.assertRegex(d.path, r'\bsimple\.txt$', 'should get a path with supplied filename')

    def test_instantiate_with_valid_multi_level_path(self):
        d = ExampleData('stuff', 'simple.txt')
        self.assertIsNotNone(d, 'should get an example data object')
        self.assertRegex(d.path, r'\bsimple\.txt$', 'should get a path with supplied filename components')

    def test_content_with_valid_file(self):
        d = ExampleData('example.txt')
        self.assertEqual(d.text_content, '# Example Data\n', 'should get fixture file contents')

    def test_content_with_invalid_file(self):
        d = ExampleData('no_such_file.txt')
        with self.assertRaises(IOError, msg='should raise exception reading nonexistent file'):
            d.text_content()
