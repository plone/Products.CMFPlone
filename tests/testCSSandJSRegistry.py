#
# CSSRegistry tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.ResourceRegistries.config import CSSTOOLNAME, JSTOOLNAME
from Products.CMFCore.utils import getToolByName


class TestCSSRegistry(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, CSSTOOLNAME)

    def testToolExists(self):
        self.failUnless(CSSTOOLNAME in self.portal.objectIds())

    def testDefaultCssIsInstalled(self):
        installedStylesheetIds = [i['id'] for i in self.tool.getResources()]
        expected = ['ploneCustom.css',
                    'ploneAuthoring.css', 
                    'plonePublic.css',
                    'ploneBase.css',
                    'ploneGenerated.css',
                    'ploneMember.css',
                    'plonePrint.css',
                    'plonePresentation.css',
                    'ploneRTL.css',
                    'ploneMobile.css']
        for e in expected:
            self.failUnless(e in installedStylesheetIds, e)


class TestJSRegistry(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, JSTOOLNAME)

    def testToolExists(self):
        self.failUnless(JSTOOLNAME in self.portal.objectIds())

    def testDefaultJSIsInstalled(self):
        installedScriptIds = [i['id'] for i in self.tool.getResources()]
        for s in installedScriptIds[:]:
            installedScriptIds += self.tool.concatenatedresources.get(s)
        expected = [
             'correctPREformatting.js',
             'plone_minwidth.js',
             'calendar_formfield.js',
             'ie5fixes.js',
             'calendarpopup.js',
             'collapsiblesections.js',
             'first_input_focus.js',
             'folder_contents_filter.js',
             'fullscreenmode.js',
             'highlightsearchterms.js',
             'mark_special_links.js',
             'select_all.js',
             'styleswitcher.js',
             'livesearch.js',
             'table_sorter.js',
             'dropdown.js',
             'cssQuery.js',
             'cookie_functions.js',
             'nodeutilities.js',
             'plone_javascript_variables.js',
             'register_function.js', 
             'formUnload.js']
        for e in expected:
            self.failUnless(e in installedScriptIds, e)

    def testJSIsInsertedInPage(self):
        page = self.portal.index_html()
        self.failUnless("" in page)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCSSRegistry))
    suite.addTest(makeSuite(TestJSRegistry))
    return suite

if __name__ == '__main__':
    framework()
