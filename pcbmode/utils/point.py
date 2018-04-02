#!/usr/bin/python

from math import pi, sin, cos, radians
import decimal

import pcbmode.config as config

class Point:

    def __init__(self, x=0, y=0):
        try:
            self.sig_dig = config.cfg['significant-digits']
        except:
            self.sig_dig = 8
        self.x = round(float(x), self.sig_dig)
        self.y = round(float(y), self.sig_dig)

    def __add__(self, p):
        """ add point 'p' of type Point to current point"""
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        """ subtract point 'p' of type Point to current point"""
        return Point(self.x - p.x, self.y - p.y)

    def __repr__(self, d=2):
        """
        return a string representation; 'd' determines number
        of significant digits to display
        """
        return "[%.*f, %.*f]" % (d, self.x, d, self.y)

    def __eq__(self, p):
        """ equality attribute """
        return (self.x == p.x) and (self.y == p.y)

    def __ne__(self, p):
        """ not equal attribute """
        return not((self.x == p.x) and (self.y == p.y))

    def assign(self, x=0, y=0):
        self.x = round(float(x), self.sig_dig)
        self.y = round(float(y), self.sig_dig)
        return

    def rotate(self, deg, p):
        """ rotate the point in degrees clockwise around another point """
        rad = radians(-deg)
        cos_angle = cos(rad)
        sin_angle = sin(rad)
        x = self.x - p.x
        y = self.y - p.y
        self.x = x*cos_angle - y*sin_angle + p.x
        self.y = x*sin_angle + y*cos_angle + p.y
        return

    def round(self, d):
        """ round decimal to nearest 'd' decimal digits """
        self.x = round(self.x, d)
        self.y = round(self.y, d)
        return

    def mult(self, scalar):
        """ multiply by scalar """
        self.x *= float(scalar)
        self.y *= float(scalar)
        return
