from xml.dom.minidom import parseString
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.resources.browser.cook import cookWhenChangingSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.context import SetupEnviron
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces import IResourceRegistry
from plone.subrequest import subrequest
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME
from Products.CMFPlone.resources.exportimport.resourceregistry import ResourceRegistryNodeAdapter
from plone.resource.interfaces import IResourceDirectory


class TestResourceRegistries(PloneTestCase.PloneTestCase):

    def test_cooking_resources(self):
        registry = getUtility(IRegistry)
        bundles = registry.collectionOfInterface(IBundleRegistry,
                                                 prefix="plone.bundles")
        bundle = bundles.add('foobar')
        bundle.jscompilation = '++plone++static/foobar-compiled.js'
        bundle.csscompilation = '++plone++static/foobar-compiled.css'

        resources = registry.collectionOfInterface(IResourceRegistry,
                                                   prefix="plone.resources")
        resource = resources.add('foobar')

        resource.js = '++plone++static/foobar.js'
        bundle.resources = ['foobar']

        persistent_directory = getUtility(IResourceDirectory, name="persistent")
        if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
            persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        container.makeDirectory('static')
        directory = container['static']
        directory.writeFile('foobar.js', 'alert("Hi!");')

        cookWhenChangingSettings(self.portal, bundle)
        resp = subrequest(
            '%s/++plone++static/foobar-compiled.js' % self.portal.absolute_url())

        self.assertTrue('alert(' in resp.getBody())

    def test_cooking_missing(self):
        registry = getUtility(IRegistry)
        bundles = registry.collectionOfInterface(IBundleRegistry,
                                                 prefix="plone.bundles")
        bundle = bundles.add('foobar')
        bundle.jscompilation = '++plone++static/foobar-compiled.js'
        bundle.csscompilation = '++plone++static/foobar-compiled.css'

        resources = registry.collectionOfInterface(IResourceRegistry,
                                                   prefix="plone.resources")
        resource = resources.add('foobar')

        resource.js = '++plone++static/foobar.js'
        bundle.resources = ['foobar']

        cookWhenChangingSettings(self.portal, bundle)
        resp = subrequest(
            '%s/++plone++static/foobar-compiled.js' % self.portal.absolute_url())

        self.assertTrue('Could not find resource' in resp.getBody())

    def test_error(self):
        registry = getUtility(IRegistry)
        bundles = registry.collectionOfInterface(IBundleRegistry,
                                                 prefix="plone.bundles")
        bundle = bundles.add('foobar')
        bundle.jscompilation = '++plone++static/foobar-compiled.js'
        bundle.csscompilation = '++plone++static/foobar-compiled.css'

        resources = registry.collectionOfInterface(IResourceRegistry,
                                                   prefix="plone.resources")
        resource = resources.add('foobar')

        resource.js = '++plone++static/foobar.js'
        bundle.resources = ['foobar']

        persistent_directory = getUtility(IResourceDirectory, name="persistent")
        if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
            persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        container.makeDirectory('static')
        directory = container['static']
        directory.writeFile('foobar.js', 'sdlfk ldsf lksdjfl s')

        cookWhenChangingSettings(self.portal, bundle)
        resp = subrequest(
            '%s/++plone++static/foobar-compiled.js' % self.portal.absolute_url())

        self.assertTrue('error cooking' in resp.getBody())


class TestResourceNodeImporter(PloneTestCase.PloneTestCase):
    """Test features of registry node importer"""
    _setup_fixture = 0  # No default fixture

    def test_resource_blacklist(self):
        # Ensure that blacklisted resources aren't imported
        reg = getToolByName(self.portal, 'portal_javascripts')
        importer = ResourceRegistryNodeAdapter(reg, SetupEnviron())
        importer.resource_type = 'javascript'
        importer.registry = getUtility(IRegistry)
        importer.resource_blacklist = set(('++resource++/bad_resource.js',))
        dom = parseString("""
            <object>
                <javascript id="++resource++/bad_resource.js" enabled="true" />
            </object>
            """)
        importer._importNode(dom.documentElement)
        resources = importer.registry.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources"
        )
        js_files = [x.js for x in resources.values()]
        self.assertTrue("++resource++/bad_resource.js" not in js_files)

    def test_resource_no_blacklist(self):
        # Ensure that blacklisted resources aren't imported
        reg = getToolByName(self.portal, 'portal_javascripts')
        importer = ResourceRegistryNodeAdapter(reg, SetupEnviron())
        importer.resource_type = 'javascript'
        importer.registry = getUtility(IRegistry)
        importer.resource_blacklist = set()
        dom = parseString("""
            <object>
                <javascript id="++resource++/bad_resource.js" enabled="true" />
            </object>
            """)
        importer._importNode(dom.documentElement)
        resources = importer.registry.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources"
        )
        js_files = [x.js for x in resources.values()]
        self.assertTrue("++resource++/bad_resource.js" in js_files)
