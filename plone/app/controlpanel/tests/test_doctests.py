import doctest
from unittest import TestSuite

from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Testing.ZopeTestCase import FunctionalDocFileSuite

from plone.app.controlpanel.tests.cptc import ControlPanelTestCase
from plone.app.controlpanel.tests.cptc import UserGroupsControlPanelTestCase

setupPloneSite()

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    tests = ['calendar.txt',
             'editing.txt',
             'filter.txt',
             'mail.txt',
             'maintenance.txt',
             'security_enable_user_folder.txt',
             'search.txt',
             'site.txt',
             'skins.txt',
             'markup.txt',
             'navigation.txt',
             'types.txt',
             ]
    suite = TestSuite()

    for test in tests:
        suite.addTest(FunctionalDocFileSuite(test,
            optionflags=OPTIONFLAGS,
            package="plone.app.controlpanel.tests",
            test_class=ControlPanelTestCase))

    suite.addTest(FunctionalDocFileSuite(
        'usergroups.txt',
        optionflags=OPTIONFLAGS,
        package="plone.app.controlpanel.tests",
        test_class=UserGroupsControlPanelTestCase))

    return suite
