import doctest
import os
import glob
import unittest

from App.Common import package_home
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Products.CMFPlone.tests import PloneTestCase, GLOBALS


UNITTESTS = ['messages.txt', 'mails.txt', 'emaillogin.txt']
OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
            glob.glob(os.path.sep.join([home, '*.txt']))
            if os.path.basename(filename) not in UNITTESTS]


def test_suite():
    filenames = list_doctests()

    suites = [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='Products.CMFPlone.tests',
               test_class=PloneTestCase.FunctionalTestCase)
              for filename in filenames]

    return unittest.TestSuite(suites)
