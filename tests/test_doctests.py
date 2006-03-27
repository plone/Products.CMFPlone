"""
    CMFPlone doctests.
"""

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import FunctionalDocFileSuite
from Testing.ZopeTestCase import ZopeDocTestSuite
from Products.PloneTestCase import PloneTestCase
PloneTestCase.setupPloneSite()

def test_suite():
    return unittest.TestSuite((
        ZopeDocTestSuite('Products.CMFPlone.CatalogTool',
                                test_class=PloneTestCase.FunctionalTestCase),
        ZopeDocTestSuite('Products.CMFPlone.PloneTool',
                                test_class=PloneTestCase.FunctionalTestCase),
        ZopeDocTestSuite('Products.CMFPlone.TranslationServiceTool',
                                test_class=PloneTestCase.FunctionalTestCase),
        ZopeDocTestSuite('Products.CMFPlone.CalendarTool',
                                test_class=PloneTestCase.FunctionalTestCase),
        FunctionalDocFileSuite('webdav_index_html_put.txt',
                                package='Products.CMFPlone.tests',
                                test_class=PloneTestCase.FunctionalTestCase),
        FunctionalDocFileSuite('rendering.txt',
                                package='Products.CMFPlone.tests',
                                test_class=PloneTestCase.FunctionalTestCase),
        FunctionalDocFileSuite('messages.txt',
                                package='Products.CMFPlone.tests'),
        FunctionalDocFileSuite('forms.txt',
                                package='Products.CMFPlone.tests',
                                test_class=PloneTestCase.FunctionalTestCase),
        ))

if __name__ == '__main__':
    framework()

