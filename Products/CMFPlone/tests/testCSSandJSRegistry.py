from plone.app.testing.bbb import PloneTestCase
from Products.ResourceRegistries.config import CSSTOOLNAME, JSTOOLNAME
from Products.CMFCore.utils import getToolByName


class TestCSSRegistry(PloneTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, CSSTOOLNAME)

    def testToolExists(self):
        self.assertTrue(CSSTOOLNAME in self.portal)

    def testDefaultCssIsInstalled(self):
        installedStylesheetIds = self.tool.getResourceIds()
        expected = [
            '++resource++plone.css',
            'RTL.css',
            ]
        for e in expected:
            self.assertTrue(e in installedStylesheetIds, e)

    def testRTLShouldHaveHigherPrecedence(self):
        installedStylesheetIds = self.tool.getResourceIds()
        indexRTLStylesheet = self.tool.getResourcePosition('RTL.css')
        comes_before = ['++resource++plone.css']
        for cb in comes_before:
            self.assertTrue(cb in installedStylesheetIds[:indexRTLStylesheet],
                            cb)


class TestJSRegistry(PloneTestCase):

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, JSTOOLNAME)

    def testToolExists(self):
        self.assertTrue(JSTOOLNAME in self.portal)

    def testDefaultJSIsInstalled(self):
        installedScriptIds = self.tool.getResourceIds()
        expected = [
            '++resource++plone.js',
            'jquery.highlightsearchterms.js',
            'mark_special_links.js',
            'select_all.js',
            'styleswitcher.js',
            'table_sorter.js',
            'cookie_functions.js',
            'plone_javascript_variables.js']
        for e in expected:
            self.assertTrue(e in installedScriptIds, e)

    def testJSIsInsertedInPage(self):
        page = self.portal.index_html()
        self.assertTrue("" in page)
