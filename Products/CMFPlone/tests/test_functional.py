# -*- coding: utf-8 -*-
import doctest
import os
import glob
import unittest

import pkg_resources
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from Products.CMFPlone.tests.PloneTestCase import FunctionalTestCase
from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
)
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.testing import layered
from Testing.ZopeTestCase import ZopeDocFileSuite


UNITTESTS = ['messages.txt', 'mails.txt', 'emaillogin.txt', 'translate.txt',
             'pwreset_browser.txt']
CONTENT_TESTS = [
    'AddMoveAndDeleteDocument.txt',
    'base_tag_not_present.txt',
    'browser.txt',
    'browser_collection_views.txt']
OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

from Products.GenericSetup import EXTENSION, profile_registry

from Products.CMFCore.utils import getToolByName

at_root = pkg_resources.resource_filename('Products.Archetypes', '')


class PloneAtTestCase(PloneTestCase):
    """ Test case for #7627 (https://dev.plone.org/ticket/7627)
        Run archetypes tests in a Plone setup """

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


def test_suite():
    # Some files need to be tested with the standard functional layer.
    ignored = UNITTESTS + CONTENT_TESTS
    standard_filenames = [
        filename for filename in
        glob.glob(os.path.sep.join([os.path.dirname(__file__), '*.txt']))
        if os.path.basename(filename) not in ignored]
    suites = [layered(doctest.DocFileSuite(
              os.path.basename(filename),
              optionflags=OPTIONFLAGS,
              package='Products.CMFPlone.tests',
              ), layer=PLONE_FUNCTIONAL_TESTING)
              for filename in standard_filenames]

    # Other files need to be tested with the plone.app.contenttypes layer.
    content_filenames = [
        filename for filename in
        glob.glob(os.path.sep.join([os.path.dirname(__file__), '*.txt']))
        if os.path.basename(filename) in CONTENT_TESTS]
    suites.extend(
        [layered(doctest.DocFileSuite(
            os.path.basename(filename),
            optionflags=OPTIONFLAGS,
            package='Products.CMFPlone.tests',
            ), layer=PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING)
        for filename in content_filenames])

    # And some use Archetypes.
    suites.extend(
        [ZopeDocFileSuite(
         os.path.basename(filename),
         optionflags=OPTIONFLAGS,
         package='Products.CMFPlone.tests',
         test_class=PloneAtTestCase)
         for filename in ['translate.txt']])
    return unittest.TestSuite(suites)
