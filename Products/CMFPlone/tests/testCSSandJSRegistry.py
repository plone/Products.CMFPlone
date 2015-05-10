from plone.app.testing.bbb import PloneTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces import IResourceRegistry


class TestCSSRegistry(PloneTestCase):

    def afterSetUp(self):
        self.registry = getUtility(IRegistry)

    def testDefaultCssIsInstalled(self):
        installedResources = self.registry.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        expected = [
            '++plone++static/plone.less',
            ]
        css_files = [y for x in installedResources.values() for y in x.css]
        for e in expected:
            self.assertTrue(e in css_files, e)

    def testBundleIsInstalled(self):
        installedBundles = self.registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles")
        expected = [
            'plone',
            'plone-legacy'
            ]
        for e in expected:
            self.assertTrue(e in installedBundles.keys(), e)

    # def testRTLShouldHaveHigherPrecedence(self):
    #     installedStylesheetIds = self.tool.getResourceIds()
    #     indexRTLStylesheet = self.tool.getResourcePosition('RTL.css')
    #     comes_before = ['++resource++plone.css']
    #     for cb in comes_before:
    #         self.assertTrue(cb in installedStylesheetIds[:indexRTLStylesheet],
    #                         cb)

    def testJSIsInsertedInPage(self):
        self.registry['plone.resources.development'] = True
        self.registry['plone.bundles/plone.develop_css'] = True
        page = self.portal.index_html()
        self.assertTrue("++plone++static/plone.less" in page)


class TestJSRegistry(PloneTestCase):

    def afterSetUp(self):
        self.registry = getUtility(IRegistry)

    def testDefaultJSIsInstalled(self):
        installedResources = self.registry.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        expected = [
            '++resource++plone.js',
            'jquery.highlightsearchterms.js'
            ]
        js_files = [x.js for x in installedResources.values()]
        for e in expected:
            self.assertTrue(e in js_files, e)

    def testJSIsInsertedInPage(self):
        self.registry['plone.resources.development'] = True
        self.registry['plone.bundles/plone.develop_javascript'] = True
        page = self.portal.index_html()
        self.assertTrue("++resource++plone.js" in page)
