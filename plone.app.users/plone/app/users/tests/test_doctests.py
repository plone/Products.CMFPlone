import doctest
from unittest import TestSuite

from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.PloneTestCase.PloneTestCase import setupPloneSite

from plone.app.users.tests import TestCase

setupPloneSite()

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


class DocTestCase(TestCase):
    # just here to work around a weird error message
    pass


def test_suite():
    tests = ['flexible_user_registration.txt',
             'forms_navigationroot.txt',
             'registration_forms.txt',
             'userdata.txt',
             'userdata_prefs_user_details.txt',
             'personal_preferences.txt',
             'personal_preferences_prefs_user_details.txt',
             'password.txt'
             ]
    suite = TestSuite()
    for test in tests:
        suite.addTest(FunctionalDocFileSuite(test,
            optionflags=OPTIONFLAGS,
            package="plone.app.users.tests",
            test_class=DocTestCase))
    return suite
