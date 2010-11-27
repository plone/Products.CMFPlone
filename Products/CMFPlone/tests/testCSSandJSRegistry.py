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
        self.failUnless(CSSTOOLNAME in self.portal)

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

    def testRTLShouldHaveHigherPrecedence(self):
        installedStylesheetIds = self.tool.getResourceIds()
        indexRTLStylesheet = self.tool.getResourcePosition('RTL.css')
        comes_before = ['base.css',
                        'public.css',
                        'columns.css',
                        'authoring.css',
                        'portlets.css',
                        'controlpanel.css',
                        'print.css',
                        'mobile.css',
                        'deprecated.css',
                        'invisibles.css',
                        'forms.css',]
        for cb in comes_before:
            self.failUnless(cb in installedStylesheetIds[:indexRTLStylesheet],cb)

class TestJSRegistry(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, JSTOOLNAME)

    def testToolExists(self):
        self.failUnless(JSTOOLNAME in self.portal)

    def testDefaultJSIsInstalled(self):
        installedScriptIds = self.tool.getResourceIds()
        expected = [
             'calendar_formfield.js',
             'collapsiblesections.js',
             'first_input_focus.js',
             'jquery.highlightsearchterms.js',
             'mark_special_links.js',
             'select_all.js',
             'styleswitcher.js',
             'livesearch.js',
             'table_sorter.js',
             'dropdown.js',
             'dragdropreorder.js',
             'cookie_functions.js',
             'nodeutilities.js',
             'plone_javascript_variables.js',
             'register_function.js',
             'formUnload.js',
             'formsubmithelpers.js',
             'form_tabbing.js',
             'popupforms.js']
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
