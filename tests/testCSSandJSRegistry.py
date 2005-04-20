#
# CSSRegistry tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CSSRegistry.config import TOOLNAME, JSTOOLNAME
from Products.CMFCore.utils import getToolByName


class TestCSSRegistry(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, TOOLNAME)

    def testToolExists(self):
        self.failUnless(TOOLNAME in self.portal.objectIds())

    def testDefaultCssIsInstalled(self):
        installedStylesheetIds = [i['id'] for i in self.tool.getStylesheets()]
        expected = ['ploneCustom.css','ploneAuthoring.css', 'plonePublic.css',
                 'ploneBase.css','plonePrint.css','plonePresentation.css',
                 'ploneMobile.css']
        for e in expected:
            self.failUnless(e in installedStylesheetIds, e)


class TestJSRegistry(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, JSTOOLNAME)

    def testToolExists(self):
        self.failUnless(JSTOOLNAME in self.portal.objectIds())

    def testDefaultJSIsInstalled(self):
        installedScriptIds = [i['id'] for i in self.tool.getScripts()]
        for s in installedScriptIds[:]:
            installedScriptIds += self.tool.concatenatedscripts.get(s)
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
             'plone_menu.js',
             'cookie_functions.js',
             'nodeutilities.js',
             'plone_javascript_variables.js',
             'register_function.js']
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
