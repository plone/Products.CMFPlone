from lxml import etree
from OFS.Image import File
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.base.interfaces import IBundleRegistry
from plone.registry import field as regfield
from plone.registry import Record
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser
from Products.CMFPlone.resources import add_bundle_on_request
from Products.CMFPlone.resources import remove_bundle_on_request
from Products.CMFPlone.resources.browser.resource import REQUEST_CACHE_KEY
from Products.CMFPlone.resources.browser.resource import ScriptsView
from Products.CMFPlone.resources.browser.resource import StylesView
from Products.CMFPlone.resources.webresource import PloneScriptResource
from Products.CMFPlone.tests import PloneTestCase
from zope.component import getUtility


class TestScriptsViewlet(PloneTestCase.PloneTestCase):
    def _make_test_bundle(self, name="foobar", depends=""):
        registry = getUtility(IRegistry)

        bundles = registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles"
        )
        bundle = bundles.add(name)
        bundle.name = name
        bundle.jscompilation = f"http://foo.bar/{name}.js"
        bundle.csscompilation = f"http://foo.bar/{name}.css"
        bundle.depends = depends
        return bundle

    def test_bundle_defernot_asyncnot(self):
        self._make_test_bundle()
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        rendered = view.render()
        self.assertTrue("async=" not in rendered)
        self.assertTrue("defer=" not in rendered)

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

    def test_scripts_data_bundle_attr(self):
        scripts = ScriptsView(self.layer["portal"], self.layer["request"], None)
        self._make_test_bundle()
        scripts.update()
        result = scripts.render()
        self.assertIn('data-bundle="foobar"', result)

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

    def test_js_bundle_depends_all(self):
        # Create a test bundle, which has unspecified dependencies and is
        # rendered in order as defined.
        self._make_test_bundle(name="a")

        # Create a test bundle, which depends on "all" other and thus rendered
        # last.
        self._make_test_bundle(name="last", depends="all")

        # Create a test bundle, which has unspecified dependencies and is
        # rendered in order as defined.
        self._make_test_bundle(name="b")

        view = ScriptsView(self.layer["portal"], self.layer["request"], None)
        view.update()
        results = view.render()

        parser = etree.HTMLParser()
        parsed = etree.fromstring(results, parser)
        scripts = parsed.xpath("//script")

        # The last element is our JS, depending on "all".
        self.assertEqual(
            "http://foo.bar/last.js",
            scripts[-1].attrib["src"],
        )

        # The first resource is our JS, which was defined with unspecified
        # dependency first.
        self.assertEqual(
            "http://foo.bar/a.js",
            scripts[0].attrib["src"],
        )

        # The second resource is our JS, which was defined with unspecified
        # dependency last.
        self.assertEqual(
            "http://foo.bar/b.js",
            scripts[1].attrib["src"],
        )

        # When more bundles depend on "all", they are ordered alphabetically
        # at the end.
        self._make_test_bundle(name="x-very-last", depends="all")
        self._make_test_bundle(name="a-last", depends="all")

        # make sure cache purged
        setattr(self.layer["request"], REQUEST_CACHE_KEY, None)

        view.update()
        results = view.render()

        parsed = etree.fromstring(results, parser)
        scripts = parsed.xpath("//script")

        # All the "all" depending bundles are sorted alphabetically at the end.
        self.assertEqual(
            "http://foo.bar/x-very-last.js",
            scripts[-1].attrib["src"],
        )
        self.assertEqual(
            "http://foo.bar/last.js",
            scripts[-2].attrib["src"],
        )
        self.assertEqual(
            "http://foo.bar/a-last.js",
            scripts[-3].attrib["src"],
        )

    def test_bundle_depends_on_missing(self):
        bundle = self._make_test_bundle()
        bundle.depends = "nonexistsinbundle"
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        results = view.render()
        # bundle should be skipped when rendering
        self.assertNotIn("http://foo.bar/foobar.js", results)

    def test_resource_browser_static_resource(self):
        resource = PloneScriptResource(self.portal, resource="++resource++plone-admin-ui.js")
        self.assertIn(
            b"window.onload", resource.file_data,
        )

    def test_resource_ofs_file(self):
        self.portal["foo.js"] = File("foo.js", "Title", b'console.log()')
        resource = PloneScriptResource(self.portal, resource="foo.js")
        self.assertEqual(
            resource.file_data, b'console.log()',
        )

    def test_resource_view(self):
        resource = PloneScriptResource(self.portal, resource="@@ok")
        self.assertEqual(
            resource.file_data, b'OK',
        )

    def test_resource_bogus(self):
        resource = PloneScriptResource(self.portal, resource="I_do_not_exist")
        self.assertEqual(
            resource.file_data, b'I_do_not_exist',
        )

    def test_relative_uri_resource(self):
        bundle = self._make_test_bundle()
        bundle.jscompilation = "//foo.bar/foobar.js"
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        results = view.render()
        self.assertIn('src="//foo.bar/foobar.js"', results)


class TestStylesViewlet(PloneTestCase.PloneTestCase):
    def _make_test_bundle(self, name="foobar", depends=""):
        registry = getUtility(IRegistry)

        bundles = registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles"
        )
        bundle = bundles.add(name)
        bundle.name = name
        bundle.jscompilation = f"http://foo.bar/{name}.js"
        bundle.csscompilation = f"http://foo.bar/{name}.css"
        bundle.depends = depends
        return bundle

    def test_styles_viewlet(self):
        styles = StylesView(self.layer["portal"], self.layer["request"], None)
        styles.update()
        results = styles.render()
        self.assertIn("++theme++barceloneta/css/barceloneta.min.css", results)
        self.assertIn("http://nohost/plone/++webresource++", results)

    def test_styles_data_bundle_attr(self):
        styles = StylesView(self.layer["portal"], self.layer["request"], None)

        # add some bundle to test with
        registry = getUtility(IRegistry)

        bundles = registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles"
        )
        bundle = bundles.add("foobar")
        bundle.name = "foobar"
        bundle.jscompilation = "http://foo.bar/foobar.js"
        bundle.csscompilation = "http://foo.bar/foobar.css"
        bundle.resources = ["foobar"]

        styles.update()
        results = styles.render()
        self.assertIn('data-bundle="foobar"', results)

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

    def test_css_bundle_depends_all(self):
        # Create a test bundle, which has unspecified dependencies and is
        # rendered in order as defined.
        self._make_test_bundle(name="a")

        # Create a test bundle, which depends on "all" other and thus rendered
        # last.
        self._make_test_bundle(name="last", depends="all")

        # Create a test bundle, which has unspecified dependencies and is
        # rendered in order as defined.
        self._make_test_bundle(name="b")

        view = StylesView(self.layer["portal"], self.layer["request"], None)
        view.update()
        results = view.render()

        parser = etree.HTMLParser()
        parsed = etree.fromstring(results, parser)
        styles = parsed.xpath("//link")

        # The last element is our CSS, depending on "all".
        self.assertEqual(
            "http://foo.bar/last.css",
            styles[-1].attrib["href"],
        )

        # The second last element is the theme barceloneta theme CSS.
        self.assertTrue(
            "++theme++barceloneta/css/barceloneta.min.css" in styles[-2].attrib["href"],
        )

        # The first resource is our CSS, which was defined with unspecified
        # dependency.
        self.assertEqual(
            "http://foo.bar/a.css",
            styles[0].attrib["href"],
        )

        # The second resource is our CSS, which was defined with unspecified
        # dependency first.
        self.assertEqual(
            "http://foo.bar/b.css",
            styles[1].attrib["href"],
        )

    def test_css_bundle_depends_all_but_custom(self):
        registry = getUtility(IRegistry)

        custom_key = "plone.app.theming.interfaces.IThemeSettings.custom_css"
        registry[custom_key] = "html { background-color: red; }"

        # Create a test bundle, which depends on "all" other and thus rendered
        # after all except the custom styles.
        self._make_test_bundle(name="almost-last", depends="all")

        view = StylesView(self.layer["portal"], self.layer["request"], None)
        view.update()
        results = view.render()

        parser = etree.HTMLParser()
        parsed = etree.fromstring(results, parser)
        styles = parsed.xpath("//link")

        # The last element is are the custom styles.
        self.assertTrue(
            "@@custom.css" in styles[-1].attrib["href"],
        )

        # The second last element is now our CSS, depending on "all".
        self.assertEqual(
            "http://foo.bar/almost-last.css",
            styles[-2].attrib["href"],
        )

        # The third last element is the theme barceloneta theme CSS.
        self.assertTrue(
            "++theme++barceloneta/css/barceloneta.min.css" in styles[-3].attrib["href"],
        )


class TestExpressions(PloneTestCase.PloneTestCase):
    def logout(self):
        setattr(self.layer["request"], REQUEST_CACHE_KEY, None)
        logout()

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

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

        # test expression on different context
        self.portal.invokeFactory("File", id="test-file", file=None)
        data = {
            "jscompilation": ("http://test4.foo/test.min.js", regfield.TextLine()),
            "csscompilation": ("http://test4.foo/test.css", regfield.TextLine()),
            "expression": ("python: object.portal_type == 'File'", regfield.TextLine()),
            "enabled": (True, regfield.Bool()),
            "depends": ("", regfield.TextLine()),
            "load_async": (True, regfield.Bool()),
            "load_defer": (True, regfield.Bool()),
        }
        for key, regdef in data.items():
            record = Record(regdef[1])
            record.value = regdef[0]
            registry.records[f"plone.bundles/testbundle4.{key}"] = record

    def test_styles_authenticated(self):
        styles = StylesView(self.portal, self.layer["request"], None)
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
        self.logout()
        styles = StylesView(self.portal, self.layer["request"], None)
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

    def test_styles_on_portal_type(self):
        styles = StylesView(self.portal, self.layer["request"], None)
        styles.update()
        results = styles.render()
        # Check that special portal_type expression styles is missing on portal
        self.assertNotIn("http://test4.foo/test.css", results)
        self.assertIn("http://test3.foo/test.css", results)

        # switch context
        setattr(self.layer["request"], REQUEST_CACHE_KEY, None)
        styles = StylesView(self.portal["test-file"], self.layer["request"], None)
        styles.update()
        results = styles.render()
        # Check that special portal_type expression styles is available on context
        self.assertIn("http://test4.foo/test.css", results)
        self.assertIn("http://test3.foo/test.css", results)

    def test_scripts_authenticated(self):
        scripts = ScriptsView(self.portal, self.layer["request"], None)
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
        self.logout()
        scripts = ScriptsView(self.portal, self.layer["request"], None)
        scripts.update()
        results = scripts.render()
        # Check that standard resources are still there, signalling that
        # rendering works without throwing an exception.
        self.assertIn("++plone++static/bundle-plone/bundle.min.js", results)
        # The first one should be included, the second one not.
        # self.assertNotIn("http://test.foo/test.min.js", results)
        self.assertNotIn("http://test2.foo/member.min.js", results)
        self.assertIn("http://test3.foo/test.min.js", results)

    def test_scripts_on_portal_type(self):
        scripts = ScriptsView(self.portal, self.layer["request"], None)
        scripts.update()
        results = scripts.render()
        # Check that special portal_type expression scripts is missing on portal
        self.assertNotIn("http://test4.foo/test.min.js", results)
        self.assertIn("http://test3.foo/test.min.js", results)

        # switch context
        setattr(self.layer["request"], REQUEST_CACHE_KEY, None)
        scripts = ScriptsView(self.portal["test-file"], self.layer["request"], None)
        scripts.update()
        results = scripts.render()
        # Check that special portal_type expression scripts is available on context
        self.assertIn("http://test4.foo/test.min.js", results)
        self.assertIn("http://test3.foo/test.min.js", results)

    def test_scripts_switching_roles(self):
        scripts = ScriptsView(self.portal, self.layer["request"], None)
        scripts.update()
        results = scripts.render()
        self.assertIn("http://test2.foo/member.min.js", results)

        self.logout()

        scripts = ScriptsView(self.portal, self.layer["request"], None)
        scripts.update()
        results = scripts.render()
        self.assertNotIn("http://test2.foo/member.min.js", results)


class TestRRControlPanel(PloneTestCase.PloneTestCase):
    def setUp(self):
        self.portal = self.layer["portal"]
        self.app = self.layer["app"]
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        )
        self.browser.open(
            self.portal.absolute_url() + "/@@resourceregistry-controlpanel"
        )

    def test_controlpanel(self):
        self.assertIn(
            '<h1 class="documentFirstHeading">Resource Registry</h1>',
            self.browser.contents,
        )
        self.assertIn(
            "++plone++static/bundle-plone/bundle.min.js", self.browser.contents
        )

    def test_add_resource(self):
        # the last form is the add form
        add_form = self.browser.getForm(index=5)
        add_form.getControl(name="name").value = "my-resource"
        add_form.getControl(name="jscompilation").value = "++resource++my.resource.js"
        add_form.getControl(name="enabled").value = "checked"
        add_form.getControl("add").click()

        self.assertIn(
            '<h2 class="accordion-header" id="heading-my-resource">',
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
            '<h2 class="accordion-header" id="heading-new-resource-name">',
            self.browser.contents,
        )
