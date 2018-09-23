# -*- coding: utf-8 -*-
from plone.app.testing import logout
from plone.registry.interfaces import IRegistry
from plone.resource.interfaces import IResourceDirectory
from plone.subrequest import subrequest
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser.resourceregistry import OverrideFolderManager  # noqa
from Products.CMFPlone.controlpanel.browser.resourceregistry import ResourceRegistryControlPanelView  # noqa
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces import IResourceRegistry
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME  # noqa
from Products.CMFPlone.resources import add_bundle_on_request
from Products.CMFPlone.resources import add_resource_on_request
from Products.CMFPlone.resources import remove_bundle_on_request
from Products.CMFPlone.resources.browser.cook import cookWhenChangingSettings
from Products.CMFPlone.resources.browser.scripts import ScriptsView
from Products.CMFPlone.resources.browser.styles import StylesView
from Products.CMFPlone.resources.bundle import Bundle
from Products.CMFPlone.resources.exportimport.resourceregistry import ResourceRegistryNodeAdapter  # noqa
from Products.CMFPlone.tests import PloneTestCase
from Products.GenericSetup.context import SetupEnviron
from xml.dom.minidom import parseString
from zope.component import getUtility

import json
import mock


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
        resource.css = ['++plone++static/foobar.css']
        bundle.resources = ['foobar']

        persistent_directory = getUtility(
            IResourceDirectory, name="persistent")
        if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
            persistent_directory.makeDirectory(
                OVERRIDE_RESOURCE_DIRECTORY_NAME)
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        container.makeDirectory('static')
        directory = container['static']
        directory.writeFile('foobar.js', 'alert("Hi!");\n\nalert("Ho!");')
        directory.writeFile('foobar.css', 'body {\ncolor: blue;\n}')

        cookWhenChangingSettings(self.portal, bundle)

        resp_js = subrequest(
            '{0}/++plone++static/foobar-compiled.js'.format(
                self.portal.absolute_url()
            )
        )
        self.assertIn(b'alert("Hi!");alert("Ho!");', resp_js.getBody())

        resp_css = subrequest(
            '{0}/++plone++static/foobar-compiled.css'.format(
                self.portal.absolute_url()
            )
        )
        self.assertIn(b'body{color:blue}', resp_css.getBody())

    def test_dont_minify_already_minified(self):
        registry = getUtility(IRegistry)
        bundles = registry.collectionOfInterface(IBundleRegistry,
                                                 prefix="plone.bundles")
        bundle = bundles.add('foobar')
        bundle.jscompilation = '++plone++static/foobar-compiled.js'
        bundle.csscompilation = '++plone++static/foobar-compiled.css'

        resources = registry.collectionOfInterface(IResourceRegistry,
                                                   prefix="plone.resources")
        resource = resources.add('foobar')

        resource.js = '++plone++static/foobar.min.js'
        resource.css = ['++plone++static/foobar.min.css']
        bundle.resources = ['foobar']

        persistent_directory = getUtility(
            IResourceDirectory, name="persistent")
        if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
            persistent_directory.makeDirectory(
                OVERRIDE_RESOURCE_DIRECTORY_NAME)
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        container.makeDirectory('static')
        directory = container['static']
        directory.writeFile('foobar.min.js', b'alert("Hi!");\n\nalert("Ho!");')
        directory.writeFile('foobar.min.css', b'body {\ncolor: blue;\n}')

        cookWhenChangingSettings(self.portal, bundle)

        resp_js = subrequest(
            '{0}/++plone++static/foobar-compiled.js'.format(
                self.portal.absolute_url()
            )
        )
        self.assertIn(b'alert("Hi!");\n\nalert("Ho!");', resp_js.getBody())

        resp_css = subrequest(
            '{0}/++plone++static/foobar-compiled.css'.format(
                self.portal.absolute_url()
            )
        )
        self.assertIn(b'body {\ncolor: blue;\n}', resp_css.getBody())

    def test_cook_only_css(self):
        registry = getUtility(IRegistry)
        bundles = registry.collectionOfInterface(IBundleRegistry,
                                                 prefix="plone.bundles")
        bundle = bundles.add('foobar')
        bundle.jscompilation = ''
        bundle.csscompilation = '++plone++static/foobar-compiled.css'

        resources = registry.collectionOfInterface(IResourceRegistry,
                                                   prefix="plone.resources")
        resource = resources.add('foobar')

        resource.css = ['++plone++static/foobar.min.css']
        bundle.resources = ['foobar']

        persistent_directory = getUtility(
            IResourceDirectory, name="persistent")
        if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
            persistent_directory.makeDirectory(
                OVERRIDE_RESOURCE_DIRECTORY_NAME)
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        container.makeDirectory('static')
        directory = container['static']
        directory.writeFile('foobar.min.css', 'body {\ncolor: red;\n}')

        cookWhenChangingSettings(self.portal, bundle)

        resp_css = subrequest(
            '{0}/++plone++static/foobar-compiled.css'.format(
                self.portal.absolute_url()
            )
        )
        self.assertIn(b'body {\ncolor: red;\n}', resp_css.getBody())

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

        bundle = Bundle(bundle)

        cookWhenChangingSettings(self.portal, bundle)
        resp = subrequest(
            '{0}/++plone++static/foobar-compiled.js'.format(
                self.portal.absolute_url()
            )
        )
        self.assertIn(b'Could not find resource', resp.getBody())

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

        persistent_directory = getUtility(
            IResourceDirectory, name="persistent")
        if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
            persistent_directory.makeDirectory(
                OVERRIDE_RESOURCE_DIRECTORY_NAME)
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        container.makeDirectory('static')
        directory = container['static']
        directory.writeFile('foobar.js', 'sdlfk ldsf lksdjfl s')

        cookWhenChangingSettings(self.portal, bundle)
        resp = subrequest(
            '{0}/++plone++static/foobar-compiled.js'.format(
                self.portal.absolute_url()
            )
        )
        self.assertIn(b'error cooking', resp.getBody())


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
            IBundleRegistry,
            prefix="plone.bundles",
            check=False
        )['plone-legacy']

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
        self.assertIn(b"++resource++/bad_resource.js", js_files)
        self.assertNotIn(
            b"resource-bad_resource-js",
            self._get_legacy_bundle().resources,
        )

    def test_resource_no_blacklist(self):
        importer = self._get_importer()
        dom = self._get_resource_dom()
        importer._importNode(dom.documentElement)
        js_files = [x.js for x in self._get_resources().values()]
        self.assertTrue("++resource++/resource.js" in js_files)
        self.assertTrue(
            "resource-resource-js" in self._get_legacy_bundle().resources)

    def test_insert_again(self):
        importer = self._get_importer()
        dom = self._get_resource_dom()
        num_resources = self._get_legacy_bundle().resources[:]
        importer._importNode(dom.documentElement)
        self.assertEqual(len(num_resources) + 1,
                          len(self._get_legacy_bundle().resources))
        importer._importNode(dom.documentElement)
        self.assertEqual(len(num_resources) + 1,
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

        self.assertEqual(len(resources) - 1,
                          len(self._get_legacy_bundle().resources))
        self.assertEqual(len(js_files) - 1,
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
        self.assertEqual(
            resources.index('one') + 1,
            resources.index('foobar-js')
        )

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
        self.assertEqual(
            resources.index('one') - 1,
            resources.index('foobar-js')
        )

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

        self.assertEqual(len(resources) - 1,
                          len(self._get_legacy_bundle().resources))
        self.assertEqual(len(js_files),
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
        self.assertEqual(str(value), 'foobar')

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
        match = b"""
.foo {
    background-image: url("../foobar.css");
}
.bar {
    background-image: url("bar/foobar.css");
}
.foobar {
    background-image: url("../foo/bar/foobar.css");
}"""
        self.assertEqual(value.data, match)

    def test_get_require_js_config_uses_stub_modules(self):
        view = ResourceRegistryControlPanelView(
            self.portal, self.layer['request'])
        self.layer['request'].form['bundle'] = 'plone-logged-in'
        config = json.loads(view.js_build_config())
        self.assertEqual(config['paths']['jquery'], 'empty:')


class DummyResource(object):
    def __init__(self, name):
        self.js = name
        self.css = [name, ]


class DummyBundle(object):
    def __init__(self, name, enabled=True):
        self.__prefix__ = 'test/' + name
        self.compile = True
        self.conditionalcomment = None
        self.csscompilation = '++resource++' + name + '.css'
        self.depends = None
        self.enabled = enabled
        self.expression = None
        self.jscompilation = '++resource++' + name + '.js'
        self.last_compilation = '123'
        self.resources = []


class TestScriptsViewlet(PloneTestCase.PloneTestCase):

    def test_scripts_viewlet(self):
        scripts = ScriptsView(
            self.layer['portal'],
            self.layer['request'],
            None
        )
        scripts.update()
        results = scripts.scripts()
        self.assertEqual(results[0]['bundle'], 'production')
        self.assertTrue(results[0]['src'].startswith(
            'http://nohost/plone/++plone++production/++unique++'))
        self.assertTrue(results[0]['src'].endswith('/default.js'))
        self.assertEqual(results[1]['bundle'], 'production')
        self.assertTrue(results[1]['src'].startswith(
            'http://nohost/plone/++plone++production/++unique++'))
        self.assertTrue(results[1]['src'].endswith('/logged-in.js'))
        self.assertEqual(len(results), 2)

    def test_scripts_viewlet_anonymous(self):
        logout()
        scripts = ScriptsView(
            self.layer['portal'],
            self.layer['request'],
            None
        )
        scripts.update()
        results = scripts.scripts()
        self.assertEqual(results[0]['bundle'], 'production')
        self.assertTrue(results[0]['src'].startswith(
            'http://nohost/plone/++plone++production/++unique++'))
        self.assertTrue(results[0]['src'].endswith('/default.js'))
        self.assertEqual(len(results), 1)

    @mock.patch.object(
        ScriptsView,
        'get_resources',
        new=lambda self: {'foo': DummyResource('++resource++foo.js')}
    )
    def test_request_resources(self):
        add_resource_on_request(self.layer['request'], 'foo')
        scripts = ScriptsView(
            self.layer['portal'],
            self.layer['request'],
            None
        )
        scripts.update()
        results = scripts.scripts()
        self.assertEqual(
            results[-1], {'src': 'http://nohost/plone/++resource++foo.js',
                          'conditionalcomment': '',
                          'resetrjs': False,
                          'bundle': 'none'})

    def test_request_resources_not_add_same_twice(self):
        req = self.layer['request']
        add_resource_on_request(req, 'foo')
        add_resource_on_request(req, 'foo')

        self.assertEqual(len(req.enabled_resources), 1)

    def test_request_bundles_not_add_same_twice(self):
        req = self.layer['request']
        add_bundle_on_request(req, 'foo')
        add_bundle_on_request(req, 'foo')

        self.assertEqual(len(req.enabled_bundles), 1)

    @mock.patch.object(
        ScriptsView,
        'get_bundles',
        new=lambda self: {'foo': Bundle(DummyBundle('foo', enabled=False))}
    )
    def test_add_bundle_on_request_with_subrequest(self):
        req = self.layer['request']

        # create a subrequest.
        subreq = req.clone()
        subreq['PARENT_REQUEST'] = req

        # add a bundle via the main request
        add_bundle_on_request(req, 'foo')

        scripts = ScriptsView(self.layer['portal'], subreq, None)

        # Send resource registry in development mode
        # Via a fake registry to allow accessing like this:
        # self.registry.records['plone.resources.development'].value
        scripts.registry = type(
            'reg',
            (object, ),
            {'records': {
                'plone.resources.development': type(
                    'val',
                    (object, ),
                    {'value': True}
                )()
            }}
        )()
        self.assertTrue(scripts.development)

        scripts.update()
        results = scripts.scripts()
        self.assertEqual(
            results[-1],
            {
                'src': 'http://nohost/plone/++resource++foo.js?version=123',
                'conditionalcomment': None,
                'bundle': 'foo'
            }
        )

    @mock.patch.object(
        ScriptsView,
        'get_bundles',
        new=lambda self: {'foo': Bundle(DummyBundle('foo', enabled=True))}
    )
    def test_remove_bundle_on_request_with_subrequest(self):
        req = self.layer['request']

        # create a subrequest.
        subreq = req.clone()
        subreq['PARENT_REQUEST'] = req

        # remove the enabled 'foo' bundle
        remove_bundle_on_request(req, 'foo')

        scripts = ScriptsView(self.layer['portal'], subreq, None)

        # Send resource registry in development mode
        # Via a fake registry to allow accessing like this:
        # self.registry.records['plone.resources.development'].value
        scripts.registry = type(
            'reg',
            (object, ),
            {'records': {
                'plone.resources.development': type(
                    'val',
                    (object, ),
                    {'value': True}
                )()
            }}
        )()
        self.assertTrue(scripts.development)

        scripts.update()
        results = scripts.scripts()
        self.assertEqual(
            [i for i in results if 'foo' in i['src']],
            []
        )

    @mock.patch.object(
        ScriptsView,
        'get_resources',
        new=lambda self: {'foo': DummyResource('++resource++foo.js')}
    )
    @mock.patch.object(
        StylesView,
        'get_resources',
        new=lambda self: {'foo': DummyResource('++resource++foo.css')}
    )
    def test_add_resource_on_request_with_subrequest(self):
        """Check, if a resource added at a main request is picked up from a
        subrequest for creating the header scripts section.
        """
        req = self.layer['request']

        # create a subrequest.
        subreq = req.clone()
        subreq['PARENT_REQUEST'] = req

        # add a resource to main request
        add_resource_on_request(req, 'foo')

        scripts = ScriptsView(self.layer['portal'], subreq, None)
        scripts.update()
        results = scripts.scripts()
        self.assertEqual(
            results[-1],
            {
                'src': 'http://nohost/plone/++resource++foo.js',
                'conditionalcomment': '',
                'resetrjs': False,
                'bundle': 'none',
            }
        )

        styles = StylesView(self.layer['portal'], subreq, None)
        styles.update()
        results = styles.styles()
        self.assertEqual(
            filter(lambda it: 'foo' in it['src'], results)[0],
            {
                'src': 'http://nohost/plone/++resource++foo.css',
                'conditionalcomment': '',
                'rel': 'stylesheet',
                'bundle': 'none',
            }
        )
