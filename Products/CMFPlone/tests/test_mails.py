"""
Mail related doctests
"""

import unittest
from zope.testing import doctest

from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFPlone.tests.utils import MockMailHost

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

class MockMailHostTestCase(PloneTestCase.FunctionalContentLessTestCase):

    def afterSetUp(self):
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = MockMailHost('MailHost')

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost


def test_suite():
    return unittest.TestSuite((
        FunctionalDocFileSuite('mails.txt',
                               optionflags=OPTIONFLAGS,
                               package='Products.CMFPlone.tests',
                               test_class=MockMailHostTestCase),
        ))
