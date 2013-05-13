import doctest
import os
import glob
import unittest

import pkg_resources
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Products.CMFPlone.tests import PloneTestCase


UNITTESTS = ['messages.txt', 'mails.txt', 'emaillogin.txt', 'translate.txt']
OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

from Products.GenericSetup import EXTENSION, profile_registry

from Products.CMFCore.utils import getToolByName

at_root = pkg_resources.resource_filename('Products.Archetypes', '')


class PloneAtTestCase(PloneTestCase.FunctionalTestCase):
    """Test case for #7627 (https://dev.plone.org/ticket/7627)
    Run archetypes tests in a Plone setup
    to have "content-slot" not defined in CMFDefault."""
    def afterSetUp(self):
        profile_registry.registerProfile(
            'Archetypes_sampletypes',
            'Archetypes Sample Content Types',
            'Extension profile incl. Archetypes sample content types',
            os.path.join(at_root, 'profiles/sample_types'),
            'Products.Archetypes',
            EXTENSION
        )
        setup = getToolByName(self.portal, 'portal_setup')
        setup.runAllImportStepsFromProfile(
            'profile-Products.Archetypes:'
            'Archetypes_sampletypes')


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
    suites.extend(
        [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='Products.CMFPlone.tests',
               test_class=PloneAtTestCase)
         for filename in ['translate.txt']])
    return unittest.TestSuite(suites)


