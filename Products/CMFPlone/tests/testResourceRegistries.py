from plone.app.testing import logout
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.base.interfaces import IBundleRegistry
from plone.registry import field as regfield
from plone.registry import Record
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser
from Products.CMFPlone.resources import add_bundle_on_request
from Products.CMFPlone.resources import remove_bundle_on_request
from Products.CMFPlone.resources.browser.resource import ScriptsView
from Products.CMFPlone.resources.browser.resource import StylesView
from Products.CMFPlone.tests import PloneTestCase
from zope.component import getUtility


class TestScriptsViewlet(PloneTestCase.PloneTestCase):
    def _make_test_bundle(self):
        registry = getUtility(IRegistry)

        bundles = registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles"
        )
        bundle = bundles.add("foobar")
        bundle.name = "foobar"
        bundle.jscompilation = "http://foo.bar/foobar.js"
        bundle.csscompilation = "http://foo.bar/foobar.css"
        bundle.resources = ["foobar"]
        return bundle

    def test_bundle_defernot_asyncnot(self):
        bundle = self._make_test_bundle()
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        rendered = view.render()
        self.assertTrue("async=" not in rendered)
        self.assertTrue("defer=" not in rendered)

    def test_bundle_defernot_async(self):
        bundle = self._make_test_bundle()
        bundle.load_async = True
        bundle.load_defer = False
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        rendered = view.render()

    def test_bundle_defer_asyncnot(self):
        bundle = self._make_test_bundle()
        bundle.load_async = False
        bundle.load_defer = True
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        rendered = view.render()
        self.assertTrue("async=" not in rendered)
        self.assertTrue("defer=" in rendered)

    def test_bundle_defernot_async(self):
        bundle = self._make_test_bundle()
        bundle.load_async = True
        bundle.load_defer = False
        request = self.app.REQUEST
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        rendered = view.render()
        self.assertTrue("async=" in rendered)
        self.assertTrue("defer=" not in rendered)

    def test_bundle_defer_async(self):
        bundle = self._make_test_bundle()
        bundle.load_async = True
        bundle.load_defer = True
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        rendered = view.render()
        self.assertTrue("async=" in rendered)
        self.assertTrue("defer=" in rendered)

    def test_scripts_viewlet(self):
        scripts = ScriptsView(self.layer["portal"], self.layer["request"], None)
        scripts.update()
        results = scripts.render()
        self.assertIn("++plone++static/bundle-plone/bundle.min.js", results)
        self.assertIn("http://nohost/plone/++webresource++", results)

    def test_scripts_viewlet_anonymous(self):
        logout()
        scripts = ScriptsView(self.layer["portal"], self.layer["request"], None)
        scripts.update()
        results = scripts.render()
        self.assertIn("++plone++static/bundle-plone/bundle.min.js", results)
        self.assertIn("http://nohost/plone/++webresource++", results)

    def test_request_bundles_not_add_same_twice(self):
        req = self.layer["request"]
        add_bundle_on_request(req, "foo")
        add_bundle_on_request(req, "foo")

        self.assertEqual(len(req.enabled_bundles), 1)

    def test_disabled_bundle_not_rendered(self):
        # request
        req = self.layer["request"]

        # create a subrequest.
        subreq = req.clone()
        subreq["PARENT_REQUEST"] = req

        scripts = ScriptsView(self.layer["portal"], subreq, None)

        # add some bundle to test with
        bundle = self._make_test_bundle()
        bundle.enabled = False
        scripts.update()
        result = scripts.render()
        self.assertNotIn("http://foo.bar/foobar.js", result)

    def test_add_bundle_on_request_with_subrequest(self):
        # request
        req = self.layer["request"]

        # create a subrequest.
        subreq = req.clone()
        subreq["PARENT_REQUEST"] = req

        # add a bundle via the main request
        add_bundle_on_request(req, "foobar")

        scripts = ScriptsView(self.layer["portal"], subreq, None)

        # add some bundle to test with
        bundle = self._make_test_bundle()
        bundle.enabled = False
        scripts.update()
        result = scripts.render()
        self.assertIn("http://foo.bar/foobar.js", result)

    def test_remove_bundle_on_request_with_subrequest(self):
        # request
        req = self.layer["request"]

        # create a subrequest.
        subreq = req.clone()
        subreq["PARENT_REQUEST"] = req

        # add a bundle via the main request
        add_bundle_on_request(req, "foobar")

        scripts = ScriptsView(self.layer["portal"], subreq, None)

        # add some bundle to test with
        bundle = self._make_test_bundle()
        bundle.enabled = True
        scripts.update()
        result = scripts.render()
        self.assertNotIn("http://test.foo/test.css", result)

    def test_bundle_depends(self):
        bundle = self._make_test_bundle()
        bundle.depends = "plone"
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        results = view.render()
        self.assertIn("http://foo.bar/foobar.js", results)

    def test_bundle_depends_on_multiple(self):
        bundle = self._make_test_bundle()
        bundle.depends = "plone,eventedit"
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        results = view.render()
        self.assertIn("http://foo.bar/foobar.js", results)

    def test_bundle_depends_on_missing(self):
        bundle = self._make_test_bundle()
        bundle.depends = "nonexistsinbundle"
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        results = view.render()
        # bundle should be skipped when rendering
        self.assertNotIn("http://foo.bar/foobar.js", results)


class TestStylesViewlet(PloneTestCase.PloneTestCase):
    def test_styles_viewlet(self):
        styles = StylesView(self.layer["portal"], self.layer["request"], None)
        styles.update()
        results = styles.render()
        self.assertIn("++theme++barceloneta/css/barceloneta.min.css", results)
        self.assertIn("http://nohost/plone/++webresource++", results)

    def test_styles_viewlet_anonymous(self):
        logout()
        styles = StylesView(self.layer["portal"], self.layer["request"], None)
        styles.update()
        results = styles.render()
        self.assertIn("++theme++barceloneta/css/barceloneta.min.css", results)
        self.assertIn("http://nohost/plone/++webresource++", results)

    def test_request_bundles_not_add_same_twice(self):
        req = self.layer["request"]
        add_bundle_on_request(req, "foo")
        add_bundle_on_request(req, "foo")
        self.assertEqual(len(req.enabled_bundles), 1)

    def test_add_bundle_on_request_with_subrequest(self):
        # request
        req = self.layer["request"]

        # create a subrequest.
        subreq = req.clone()
        subreq["PARENT_REQUEST"] = req

        # add a bundle via the main request
        add_bundle_on_request(req, "testbundle")

        scripts = ScriptsView(self.layer["portal"], subreq, None)

        # add some bundle to test with
        registry = getUtility(IRegistry)
        data = {
            "jscompilation": ("http://test.foo/test.min.js", regfield.TextLine()),
            "csscompilation": ("http://test.foo/test.css", regfield.TextLine()),
            "expression": ("", regfield.TextLine()),
            "enabled": (False, regfield.Bool()),
            "depends": ("", regfield.TextLine()),
            "load_async": (True, regfield.Bool()),
            "load_defer": (True, regfield.Bool()),
        }
        for key, regdef in data.items():
            record = Record(regdef[1])
            record.value = regdef[0]
            registry.records[f"plone.bundles/testbundle.{key}"] = record

        scripts.update()
        result = scripts.render()
        self.assertIn("http://test.foo/test.min.js", result)

    def test_remove_bundle_on_request_with_subrequest(self):
        # request
        req = self.layer["request"]

        # create a subrequest.
        subreq = req.clone()
        subreq["PARENT_REQUEST"] = req

        # remove a bundle via the main request
        remove_bundle_on_request(req, "testbundle")

        scripts = ScriptsView(self.layer["portal"], subreq, None)

        # add some bundle to test with
        registry = getUtility(IRegistry)
        data = {
            "jscompilation": ("http://test.foo/test.min.js", regfield.TextLine()),
            "csscompilation": ("http://test.foo/test.css", regfield.TextLine()),
            "expression": ("", regfield.TextLine()),
            "enabled": (True, regfield.Bool()),
            "depends": ("", regfield.TextLine()),
            "load_async": (True, regfield.Bool()),
            "load_defer": (True, regfield.Bool()),
        }
        for key, regdef in data.items():
            record = Record(regdef[1])
            record.value = regdef[0]
            registry.records[f"plone.bundles/testbundle.{key}"] = record

        scripts.update()
        result = scripts.render()
        self.assertNotIn("http://test.foo/test.min.js", result)


class TestExpressions(PloneTestCase.PloneTestCase):

    def setUp(self):
        # Add three bundles with three different expressions.
        registry = getUtility(IRegistry)
        data = {
            "jscompilation": ("http://test.foo/test.min.js", regfield.TextLine()),
            "csscompilation": ("http://test.foo/test.css", regfield.TextLine()),
            "expression": ("python: False", regfield.TextLine()),
            "enabled": (True, regfield.Bool()),
            "depends": ("", regfield.TextLine()),
            "load_async": (True, regfield.Bool()),
            "load_defer": (True, regfield.Bool()),
        }
        for key, regdef in data.items():
            record = Record(regdef[1])
            record.value = regdef[0]
            registry.records[f"plone.bundles/testbundle.{key}"] = record

        data = {
            "jscompilation": ("http://test2.foo/member.min.js", regfield.TextLine()),
            "csscompilation": ("http://test2.foo/member.css", regfield.TextLine()),
            "expression": ("python: member is not None", regfield.TextLine()),
            "enabled": (True, regfield.Bool()),
            "depends": ("", regfield.TextLine()),
            "load_async": (True, regfield.Bool()),
            "load_defer": (True, regfield.Bool()),
        }
        for key, regdef in data.items():
            record = Record(regdef[1])
            record.value = regdef[0]
            registry.records[f"plone.bundles/testbundle2.{key}"] = record

        data = {
            "jscompilation": ("http://test3.foo/test.min.js", regfield.TextLine()),
            "csscompilation": ("http://test3.foo/test.css", regfield.TextLine()),
            "expression": ("python: True", regfield.TextLine()),
            "enabled": (True, regfield.Bool()),
            "depends": ("", regfield.TextLine()),
            "load_async": (True, regfield.Bool()),
            "load_defer": (True, regfield.Bool()),
        }
        for key, regdef in data.items():
            record = Record(regdef[1])
            record.value = regdef[0]
            registry.records[f"plone.bundles/testbundle3.{key}"] = record

    def test_styles_authenticated(self):
        styles = StylesView(self.layer["portal"], self.layer["request"], None)
        styles.update()
        results = styles.render()
        # Check that standard resources are still there, signalling that
        # rendering works without throwing an exception.
        self.assertIn("++theme++barceloneta/css/barceloneta.min.css", results)
        self.assertIn("http://nohost/plone/++webresource++", results)
        # Test our additional bundles.
        # self.assertNotIn("http://test.foo/test.css", results)
        self.assertIn("http://test2.foo/member.css", results)
        self.assertIn("http://test3.foo/test.css", results)

    def test_styles_anonymous(self):
        logout()
        styles = StylesView(self.layer["portal"], self.layer["request"], None)
        styles.update()
        results = styles.render()
        # Check that standard resources are still there, signalling that
        # rendering works without throwing an exception.
        self.assertIn("++theme++barceloneta/css/barceloneta.min.css", results)
        self.assertIn("http://nohost/plone/++webresource++", results)
        # Test our additional bundles.
        # self.assertNotIn("http://test.foo/test.css", results)
        self.assertNotIn("http://test2.foo/member.css", results)
        self.assertIn("http://test3.foo/test.css", results)

    def test_scripts_authenticated(self):
        scripts = ScriptsView(self.layer["portal"], self.layer["request"], None)
        scripts.update()
        results = scripts.render()
        # Check that standard resources are still there, signalling that
        # rendering works without throwing an exception.
        self.assertIn("++plone++static/bundle-plone/bundle.min.js", results)
        # The first one should be included, the second one not.
        # self.assertNotIn("http://test.foo/test.min.js", results)
        self.assertIn("http://test2.foo/member.min.js", results)
        self.assertIn("http://test3.foo/test.min.js", results)

    def test_scripts_anonymous(self):
        logout()
        scripts = ScriptsView(self.layer["portal"], self.layer["request"], None)
        scripts.update()
        results = scripts.render()
        # Check that standard resources are still there, signalling that
        # rendering works without throwing an exception.
        self.assertIn("++plone++static/bundle-plone/bundle.min.js", results)
        # The first one should be included, the second one not.
        # self.assertNotIn("http://test.foo/test.min.js", results)
        self.assertNotIn("http://test2.foo/member.min.js", results)
        self.assertIn("http://test3.foo/test.min.js", results)


class TestRRControlPanel(PloneTestCase.PloneTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            f'Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}'
        )
        self.browser.open(self.portal.absolute_url() + "/@@resourceregistry-controlpanel")

    def test_controlpanel(self):
        self.assertIn("<h1 class=\"documentFirstHeading\">Resource Registry</h1>", self.browser.contents)
        self.assertIn("++plone++static/bundle-plone/bundle.min.js", self.browser.contents)

    def test_add_resource(self):
        # the last form is the add form
        add_form = self.browser.getForm(index=5)
        add_form.getControl(name="name").value = "my-resource"
        add_form.getControl(name="jscompilation").value = "++resource++my.resource.js"
        add_form.getControl(name="enabled").value = "checked"
        add_form.getControl("add").click()

        self.assertIn(
            "<h2 class=\"accordion-header\" id=\"heading-my-resource\">",
            self.browser.contents,
        )

    def test_update_resource(self):
        # try to set already existing name should fail
        form = self.browser.getForm(index=4)
        form.getControl(name="name").value = "plone"
        form.getControl("update").click()

        self.assertIn("Record name plone already taken.", self.browser.contents)

        # set new name
        form = self.browser.getForm(index=4)
        form.getControl(name="name").value = "new-resource-name"
        form.getControl("update").click()

        self.assertIn(
             "<h2 class=\"accordion-header\" id=\"heading-new-resource-name\">",
            self.browser.contents,
        )
