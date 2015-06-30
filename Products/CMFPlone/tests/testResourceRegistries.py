from xml.dom.minidom import parseString
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.resources.browser.cook import cookWhenChangingSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.context import SetupEnviron
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces import IResourceRegistry
from Products.CMFPlone.controlpanel.browser.resourceregistry import OverrideFolderManager
from plone.subrequest import subrequest
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME
from Products.CMFPlone.resources.exportimport.resourceregistry import (
    ResourceRegistryNodeAdapter)
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

    def _get_importer(self, blacklist=set([])):
        reg = getToolByName(self.portal, 'portal_javascripts')
        importer = ResourceRegistryNodeAdapter(reg, SetupEnviron())
        importer.resource_type = 'javascript'
        importer.registry = getUtility(IRegistry)
        importer.resource_blacklist = blacklist
        return importer

    def _get_resources(self):
        return getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources"
        )

    def _get_legacy_bundle(self):
        return getUtility(IRegistry).collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles", check=False)['plone-legacy']

    def _get_resource_dom(self, name='++resource++/resource.js',
                          remove=False, enabled=True):
        return parseString("""
            <object>
                <javascript id="%s" remove="%s" enabled="%s" />
            </object>
            """ % (name, str(remove), str(enabled).lower()))

    def test_resource_blacklist(self):
        # Ensure that blacklisted resources aren't imported
        importer = self._get_importer(set(('++resource++/bad_resource.js',)))
        dom = self._get_resource_dom("++resource++/bad_resource.js")
        importer._importNode(dom.documentElement)
        js_files = [x.js for x in self._get_resources().values()]
        self.assertTrue("++resource++/bad_resource.js" not in js_files)
        self.assertTrue(
            "resource-bad_resource-js" not in self._get_legacy_bundle().resources)

    def test_resource_no_blacklist(self):
        importer = self._get_importer()
        dom = self._get_resource_dom()
        importer._importNode(dom.documentElement)
        js_files = [x.js for x in self._get_resources().values()]
        self.assertTrue("++resource++/resource.js" in js_files)
        self.assertTrue("resource-resource-js" in self._get_legacy_bundle().resources)

    def test_insert_again(self):
        importer = self._get_importer()
        dom = self._get_resource_dom()
        num_resources = self._get_legacy_bundle().resources[:]
        importer._importNode(dom.documentElement)
        self.assertEquals(len(num_resources) + 1,
                          len(self._get_legacy_bundle().resources))
        importer._importNode(dom.documentElement)
        self.assertEquals(len(num_resources) + 1,
                          len(self._get_legacy_bundle().resources))

    def test_remove(self):
        importer = self._get_importer()

        # inserter it
        dom = self._get_resource_dom()
        importer._importNode(dom.documentElement)

        resources = self._get_legacy_bundle().resources[:]
        js_files = [x.js for x in self._get_resources().values()]

        # import again
        dom = self._get_resource_dom(remove=True)
        importer._importNode(dom.documentElement)

        self.assertEquals(len(resources) - 1,
                          len(self._get_legacy_bundle().resources))
        self.assertEquals(len(js_files) - 1,
                          len([x.js for x in self._get_resources().values()]))

    def test_insert_after(self):
        importer = self._get_importer()
        one = self._get_resource_dom('one')
        two = self._get_resource_dom('two')
        three = self._get_resource_dom('three')
        importer._importNode(one.documentElement)
        importer._importNode(two.documentElement)
        importer._importNode(three.documentElement)

        # now, insert
        foobar = parseString("""
            <object>
                <javascript id="foobar.js" insert-after="one" enabled="true" />
            </object>
            """)
        importer._importNode(foobar.documentElement)
        resources = self._get_legacy_bundle().resources
        self.assertTrue(resources.index('one') + 1, resources.index('foobar-js'))

    def test_insert_before(self):
        importer = self._get_importer()
        one = self._get_resource_dom('one')
        two = self._get_resource_dom('two')
        three = self._get_resource_dom('three')
        importer._importNode(one.documentElement)
        importer._importNode(two.documentElement)
        importer._importNode(three.documentElement)

        # now, insert
        foobar = parseString("""
            <object>
                <javascript id="foobar.js" insert-before="one" enabled="true" />
            </object>
            """)
        importer._importNode(foobar.documentElement)
        resources = self._get_legacy_bundle().resources
        self.assertTrue(resources.index('one') - 1, resources.index('foobar-js'))

    def test_be_able_to_disable_but_not_remove(self):
        importer = self._get_importer()

        # inserter it
        dom = self._get_resource_dom()
        importer._importNode(dom.documentElement)

        resources = self._get_legacy_bundle().resources[:]
        js_files = [x.js for x in self._get_resources().values()]

        # import again
        dom = self._get_resource_dom(enabled=False)
        importer._importNode(dom.documentElement)

        self.assertEquals(len(resources) - 1,
                          len(self._get_legacy_bundle().resources))
        self.assertEquals(len(js_files),
                          len([x.js for x in self._get_resources().values()]))


class TestConfigJs(PloneTestCase.PloneTestCase):

    def test_init_shim_works_with_function(self):
        config = self.portal.restrictedTraverse('config.js')()
        self.assertTrue('init: function' in config)


class TestControlPanel(PloneTestCase.PloneTestCase):

    def test_save_override_file(self):
        req = self.layer['request']
        req.environ['PATH_INFO'] = '++plone++foo/bar.css'
        mng = OverrideFolderManager(self.portal)
        mng.save_file('foo/bar.css', 'foobar')
        value = self.portal.restrictedTraverse('++plone++foo/bar.css')
        self.assertEquals(str(value), 'foobar')

    def test_override_rewrite_links(self):
        req = self.layer['request']
        req.environ['PATH_INFO'] = '++plone++foo/bar.css'
        mng = OverrideFolderManager(self.portal)
        css = """
.foo {
    background-image: url("%(site_url)s/foobar.css");
}
.bar {
    background-image: url("%(site_url)s/++plone++foo/bar/foobar.css");
}
.foobar {
    background-image: url("%(site_url)s/foo/bar/foobar.css");
}""" % {'site_url': self.portal.absolute_url()}
        mng.save_file('foo/bar.css', css)
        value = self.portal.restrictedTraverse('++plone++foo/bar.css')
        match = """
.foo {
    background-image: url("../foobar.css");
}
.bar {
    background-image: url("bar/foobar.css");
}
.foobar {
    background-image: url("../foo/bar/foobar.css");
}"""
        self.assertEquals(str(value), match)