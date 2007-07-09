#
# CSSRegistry tests
#

from Products.CMFPlone.tests import PloneTestCase

from Products.ResourceRegistries.config import CSSTOOLNAME, JSTOOLNAME
from Products.CMFCore.utils import getToolByName


class TestCSSRegistry(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, CSSTOOLNAME)

    def testToolExists(self):
        self.failUnless(CSSTOOLNAME in self.portal.objectIds())

    def testDefaultCssIsInstalled(self):
        installedStylesheetIds = self.tool.getResourceIds()
        expected = ['ploneCustom.css',
                    'authoring.css', 
                    'public.css',
                    'base.css',
                    'portlets.css',
                    'deprecated.css',
                    'member.css',
                    'print.css',
                    'RTL.css',
                    'mobile.css',]
        for e in expected:
            self.failUnless(e in installedStylesheetIds, e)


class TestJSRegistry(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, JSTOOLNAME)

    def testToolExists(self):
        self.failUnless(JSTOOLNAME in self.portal.objectIds())

    def testDefaultJSIsInstalled(self):
        installedScriptIds = self.tool.getResourceIds()
        expected = [
             'calendar_formfield.js',
             'calendarpopup.js',
             'collapsiblesections.js',
             'first_input_focus.js',
             'highlightsearchterms.js',
             'mark_special_links.js',
             'select_all.js',
             'styleswitcher.js',
             'livesearch.js',
             'table_sorter.js',
             'dropdown.js',
             'dragdropreorder.js',
             'cssQuery.js',
             'cookie_functions.js',
             'nodeutilities.js',
             'plone_javascript_variables.js',
             'register_function.js', 
             'formUnload.js',
             'formsubmithelpers.js',
             'form_tabbing.js']
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
