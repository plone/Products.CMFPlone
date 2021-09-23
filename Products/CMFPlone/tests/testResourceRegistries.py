from plone.app.testing import logout
from plone.registry.interfaces import IRegistry
from plone.resource.interfaces import IResourceDirectory
from plone.subrequest import subrequest
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME
from Products.CMFPlone.resources import add_bundle_on_request
from Products.CMFPlone.resources import remove_bundle_on_request
from Products.CMFPlone.resources.browser.resource import ScriptsView
from Products.CMFPlone.resources.browser.resource import StylesView
from Products.CMFPlone.tests import PloneTestCase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from unittest import mock
from zope.component import getUtility
from plone.registry import Record
from plone.registry import field as regfield

import json
import os


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
        self.assertTrue('async=' not in rendered)
        self.assertTrue('defer=' not in rendered)

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
        self.assertTrue('async=' not in rendered)
        self.assertTrue('defer=' in rendered)

    def test_bundle_defernot_async(self):
        bundle = self._make_test_bundle()
        bundle.load_async = True
        bundle.load_defer = False
        request = self.app.REQUEST
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        rendered = view.render()
        self.assertTrue('async=' in rendered)
        self.assertTrue('defer=' not in rendered)

    def test_bundle_defer_async(self):
        bundle = self._make_test_bundle()
        bundle.load_async = True
        bundle.load_defer = True
        view = ScriptsView(self.app, self.app.REQUEST, None, None)
        view.update()
        rendered = view.render()
        self.assertTrue('async=' in rendered)
        self.assertTrue('defer=' in rendered)

    def test_scripts_viewlet(self):
        scripts = ScriptsView(self.layer["portal"], self.layer["request"], None)
        scripts.update()
        results = scripts.render()
        self.assertIn(
            "++plone++static/bundle-bootstrap/js/bootstrap.bundle.min.js", results
        )
        self.assertIn("++plone++static/bundle-plone/bundle.min.js", results)
        self.assertIn("http://nohost/plone/++webresource++", results)

    def test_scripts_viewlet_anonymous(self):
        logout()
        scripts = ScriptsView(self.layer["portal"], self.layer["request"], None)
        scripts.update()
        results = scripts.render()
        self.assertIn(
            "++plone++static/bundle-bootstrap/js/bootstrap.bundle.min.js", results
        )
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
