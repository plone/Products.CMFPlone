import doctest
from unittest import TestSuite

from Testing.ZopeTestCase import FunctionalDocFileSuite

from plone.app.portlets.tests.base import PortletsFunctionalTestCase

def test_suite():
    suite = TestSuite()
    OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    for testfile in ('testViewName.txt', 'testMemberDashboard.txt'):
        suite.addTest(FunctionalDocFileSuite(testfile,
                                optionflags=OPTIONFLAGS,
                                package="plone.app.portlets.tests",
                                test_class=PortletsFunctionalTestCase),
                     )
    return suite
