#!/usr/bin/python

from __future__ import print_function

import sys

def info(info, newline=True):
    """
    """
    if newline == True:
        print("-- %s" % info)
    else:
        sys.stdout.write("-- %s" % info)


def note(note, newline=True):
    """
    """
    if newline == True:
        print("-- NOTE: %s" % note)
    else:
        sys.stdout.write("-- NOTE: %s" % note)



def subInfo(info, newline=True):
    """
    """
    if newline == True:
        print(" * %s" % info)
    else:
        sys.stdout.write(" * %s" % info)



def progressiveInfo(info):
    """
    """
    sys.stdout.write(info)
    sys.stdout.flush()



def error(info, error_type=None):
    """
    """
    print('-----------------------------')
    print('Yikes, ERROR!')
    print('* {}'.format(info))
    print('Solder on!')
    print('-----------------------------')
    if error_type != None:
        raise error_type(info)
    raise Exception(info)




