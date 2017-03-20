try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from pcbmode.utils.style import Style
from pcbmode.config import Config

class TestStyle(unittest.TestCase):
    """Test Style module"""

    def setUp(self):
        self.c = Config(clean=True)
        self.c.load_defaults()

    def assertHasStyle(self, style, *matches):
        style_string_parts = style.getStyleString().split(';')
        for match in matches:
            with self.subTest(match=match):
                self.assertTrue(match in style_string_parts, 'style string should contain {}'.format(match))

    def test_instantiate_style(self):
        style = Style({'type': 'rect'}, 'conductor')

    def test_style_for_rect_on_conductor_layer(self):
        style = Style({'type': 'rect'}, 'conductor')
        self.assertEqual(style.getStyleType(), 'fill', 'should create fill style from conductor rect')

    def test_style_for_rect_on_outline_layer(self):
        style = Style({'type': 'rect'}, 'outline')
        self.assertEqual(style.getStyleType(), 'stroke', 'should create stroke style from outline rect')

    def test_style_for_rect_on_silkscreen_sublayer(self):
        style = Style({'type': 'rect', 'stroke-width': 0.5}, 'silkscreen', 'refdef')
        self.assertEqual(style.getStyleType(), 'stroke', 'should create stroke style from silkscreen refdef rect')

    def test_style_for_text_on_conductor_layer(self):
        style = Style({'type': 'text'}, 'conductor')
        self.assertEqual(style.getStyleType(), 'fill', 'should create fill style from conductor text')

    def test_style_for_text_on_silkscreen_layer(self):
        style = Style({'type': 'text'}, 'silkscreen')
        self.assertEqual(style.getStyleType(), 'fill', 'should create fill style from silkscreen text')

    def test_style_for_rect_on_conductor_layer_with_style(self):
        style = Style({'type': 'rect', 'style': 'fill'}, 'conductor')
        self.assertEqual(style.getStyleType(), 'fill', 'should create fill style from conductor rect with explicit fill style')

    def test_style_for_rect_on_silkscreen_layer_with_style(self):
        style = Style({'type': 'rect', 'style': 'stroke', 'stroke-width': 0.5}, 'silkscreen')
        self.assertEqual(style.getStyleType(), 'stroke', 'should create stroke style from silkscreen rect with explicity stroke style')
        self.assertHasStyle(style, 'stroke-width:0.5')

    def test_style_for_rect_on_conductor_layer_with_dict_none(self):
        """When no style or layer style available, use global default style for this layer"""
        self.c.stl['layout']['conductor'] = None
        style = Style({'type': 'rect'}, 'conductor')

    def test_style_for_rect_on_outline_layer_with_dict_none(self):
        """When no style or layer style available, use global default style for this layer"""
        self.c.stl['layout']['outline'] = None
        style = Style({'type': 'rect', 'stroke-width': 0.5}, 'outline')
        self.assertHasStyle(style, 'stroke-width:0.5')

    def test_explicit_stroke_width(self):
        """If a stroke-width is supplied in the shape dict, it should be used"""
        style = Style({'type': 'rect', 'style': 'stroke', 'stroke-width': 0.9}, 'silkscreen')
        self.assertEqual(style.getStrokeWidth(), 0.9, 'should set stroke width from shape dict')
        self.assertHasStyle(style, 'stroke-width:0.9')

    def test_default_stroke_width(self):
        """If no stroke-width is supplied in the shape dict, it should be set from the layout style"""
        style = Style({'type': 'rect'}, 'outline')
        self.assertEqual(style.getStrokeWidth(), 0.05, 'should set default stroke width from layout style')
        self.assertHasStyle(style, 'stroke-width:0.05')

    @patch('pcbmode.utils.messages.error')
    def test_unknown_style_for_rect_on_silkscreen_sublayer(self, e):
        style = Style({'type': 'rect', 'style': 'unknown', 'stroke-width': 0.5}, 'silkscreen', 'refdef')
        self.assertTrue(e.called)
        self.assertRegex(e.call_args[0][0], r"Encountered an unknown 'style' type")

