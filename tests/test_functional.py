"""
    CMFPlone functional doctests.  This module collects all *.txt
    files in the tests directory and runs them.

    See also ``test_doctests.py``.

"""

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import glob
from zope.testing import doctest
import unittest
from Globals import package_home
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Products.CMFPlone.tests import PloneTestCase, GLOBALS

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
            glob.glob(os.path.sep.join([home, '*.txt']))]

def test_suite():
    filenames = list_doctests()

    return unittest.TestSuite(
        [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='Products.CMFPlone.tests',
               test_class=PloneTestCase.FunctionalTestCase)
         for filename in filenames]
        )

if __name__ == '__main__':
    framework()

