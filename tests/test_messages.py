import io

try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pcbmode.utils import messages as msg

class TestMessages(unittest.TestCase):
    """Test message functions"""

    # info tests
    def test_info_with_default_newline(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            msg.info('some information')
            self.assertEqual(fake_out.getvalue(), '-- some information\n')

    def test_info_with_specified_newline(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            msg.info('some information', newline=True)
            self.assertEqual(fake_out.getvalue(), '-- some information\n')

    def test_info_with_no_newline(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            msg.info('some information', newline=False)
            self.assertEqual(fake_out.getvalue(), '-- some information')

    # note tests
    def test_note_with_default_newline(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            msg.note('a note')
            self.assertEqual(fake_out.getvalue(), '-- NOTE: a note\n')

    def test_note_with_specified_newline(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            msg.note('a note', newline=True)
            self.assertEqual(fake_out.getvalue(), '-- NOTE: a note\n')

    def test_note_with_no_newline(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            msg.note('a note', newline=False)
            self.assertEqual(fake_out.getvalue(), '-- NOTE: a note')

    # subInfo tests
    def test_sub_info_with_default_newline(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            msg.subInfo('some sub-information')
            self.assertEqual(fake_out.getvalue(), ' * some sub-information\n')

    def test_sub_info_with_specified_newline(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            msg.subInfo('some sub-information', newline=True)
            self.assertEqual(fake_out.getvalue(), ' * some sub-information\n')

    def test_sub_info_with_no_newline(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            msg.subInfo('some sub-information', newline=False)
            self.assertEqual(fake_out.getvalue(), ' * some sub-information')

    # progressiveInfo tests
    def test_progressive_info(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            msg.progressiveInfo('progress...')
            self.assertEqual(fake_out.getvalue(), 'progress...')
            msg.progressiveInfo('.')
            self.assertEqual(fake_out.getvalue(), 'progress....')

    def test_error_without_type(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            with self.assertRaisesRegex(Exception, r'error details', msg='error should raise Exception'):
                msg.error('error details')
            self.assertEqual(fake_out.getvalue(),
                    '-----------------------------\n'
                    'Yikes, ERROR!\n'
                    '* error details\n'
                    'Solder on!\n'
                    '-----------------------------\n')

    def test_error_with_type(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            with self.assertRaisesRegex(TypeError, r'custom error details', msg='error should raise error of specified type'):
                msg.error('custom error details', error_type=TypeError)
            self.assertEqual(fake_out.getvalue(),
                    '-----------------------------\n'
                    'Yikes, ERROR!\n'
                    '* custom error details\n'
                    'Solder on!\n'
                    '-----------------------------\n')

if __name__ == '__main__':
    unittest.main()
