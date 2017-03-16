import unittest

from pcbmode.utils.svgparser import SvgParser

parseAll=True

class TestSvgParser(unittest.TestCase):

    def setUp(self):
        self.g = SvgParser.grammar()

    def test_parse_simple_path(self):
        paths = [
            'M3,4z',
            'm5,6z',
            'm1,5 6,7 8,9 z',
            'M600,350 l 50,-25',
            'm0 0 a10,10 10 0 0 10,10',
            'm0,0t1,2,3,4,5,6',
            'M600,350 l 50,-25 a25,25 -30 0,1 50,-25 l 50,-25 a25,50 -30 0,1 50,-25 l 50,-25 a25,75 -30 0,1 50,-25 l 50,-25 a25,100 -30 0,1 50,-25 l 50,-25',
        ]
        for path in paths:
            with self.subTest(path=path):
                result = self.g.parseString(path, parseAll=parseAll)
                print("{}".format(path))
                for res in result:
                    print(" * {}".format(res))
