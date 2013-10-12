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
        expected = ['ploneCustom.css',
                    'authoring.css',
                    'public.css',
                    'base.css',
                    'portlets.css',
                    'deprecated.css',
                    'member.css',
                    'print.css',
                    'RTL.css',
                    'mobile.css', ]
        for e in expected:
            self.assertTrue(e in installedStylesheetIds, e)

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
                        'forms.css', ]
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
            'modernizr.js',
            'formUnload.js',
            'formsubmithelpers.js',
            'form_tabbing.js',
            'popupforms.js']
        for e in expected:
            self.assertTrue(e in installedScriptIds, e)

    def testJSIsInsertedInPage(self):
        page = self.portal.index_html()
        self.assertTrue("" in page)
