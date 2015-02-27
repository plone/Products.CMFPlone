from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.resources.browser.cook import cookWhenChangingSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces import IResourceRegistry
from plone.subrequest import subrequest
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME
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
