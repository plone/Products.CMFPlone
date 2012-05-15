import doctest
import os
import glob
import unittest

from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Products.CMFPlone.tests import PloneTestCase


UNITTESTS = ['messages.txt', 'mails.txt', 'emaillogin.txt']
OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def list_doctests():
    return [filename for filename in
            glob.glob(os.path.sep.join([os.path.dirname(__file__), '*.txt']))
            if os.path.basename(filename) not in UNITTESTS]


def test_suite():
    filenames = list_doctests()

    suites = [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='Products.CMFPlone.tests',
               test_class=PloneTestCase.FunctionalTestCase)
              for filename in filenames]

    return unittest.TestSuite(suites)
