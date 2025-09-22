from plone.registry.interfaces import IRegistry
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from unittest import mock
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class TestMainTemplate(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"].clone()

    @property
    def view(self):
        return getMultiAdapter((self.portal, self.request), name="main_template")

    def test_request_containment(self):
        """Very basic test to show that the following works:
        `"ajax_load" in request`
        instead of:
        `request.get("ajax_load", MARKER) is not MARKER1`
        """
        self.request.form["ajax_load"] = True
        self.assertTrue("ajax_load" in self.request.form)
        self.assertTrue("ajax_load" in self.request)

    def test_use_ajax_default(self):
        """Default use_ajax should be False."""
        self.assertFalse(self.view.use_ajax())

    def test_use_ajax_xhr(self):
        """Return `True` for XHR requests, if all conditions are met."""
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

        # Patch registry record `plone.use_ajax_main_template` to return True
        with mock.patch("plone.registry.registry.Registry.get", return_value=True):
            self.assertTrue(self.view.use_ajax())

    def test_use_ajax_xhr_disabled(self):
        """Return `False` for XHR requests, if setting is off."""
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.assertFalse(self.view.use_ajax())

    def test_use_ajax_ajax_load(self):
        """use_ajax can be explicitly set via ajax_load."""
        self.request.set("ajax_load", True)
        self.assertTrue(self.view.use_ajax())

    def test_use_ajax_ajax_load_other_true(self):
        """ajax_load understands also other forms of `True`."""
        self.request.set("ajax_load", "on")
        self.assertTrue(self.view.use_ajax())

    def test_use_ajax_ajax_load_query(self):
        """The ajax_load parameter can also be set as request parameter.
        Actually, this would be the typical and default case.
        """
        self.request.form["ajax_load"] = "yes"
        self.assertTrue(self.view.use_ajax())

    def test_use_ajax_ajax_load_precedence(self):
        """The ajax_load parameter always takes precedence."""
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.request.form["ajax_load"] = "off"

        # Patch registry record `plone.use_ajax_main_template` to return True
        with mock.patch("plone.registry.registry.Registry.get", return_value=True):
            self.assertFalse(self.view.use_ajax())

    def test_main_template_standard(self):
        """Test the standard case to use the main_template.pt."""
        self.assertIn("/main_template.pt", self.view.template.filename)

    def test_main_template_ajax_parameter(self):
        """Test, if an explicitly set `ajax_load` URL parameter leads to use
        the ajax_main_template.pt.
        """
        self.request.form["ajax_load"] = True
        self.assertIn("/ajax_main_template.pt", self.view.template.filename)

    def test_main_template_ajax_manually(self):
        """Test, if an explicitly set `ajax_load` request parameter leads to
        use the ajax_main_template.pt.
        """
        self.request.set("ajax_load", True)
        self.assertIn("/ajax_main_template.pt", self.view.template.filename)

    def test_main_template_auto(self):
        """Test, if an AJAX request leads to the ajax_main_template.pt."""
        registry = getUtility(IRegistry)
        registry["plone.use_ajax_main_template"] = True
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.assertIn("/ajax_main_template.pt", self.view.template.filename)

    def test_main_template_noauto_if_set(self):
        """Test a falsy ajax_load value and a AJAX request forces to use the
        normal main_template and not the ajax_main_template.pt.
        """
        registry = getUtility(IRegistry)
        registry["plone.use_ajax_main_template"] = True
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.request.form["ajax_load"] = "False"
        self.assertIn("/main_template.pt", self.view.template.filename)

    def test_main_template_no_ajax_1(self):
        """Test a falsy ajax_load value does not lead to ajax_main_template.pt."""
        registry = getUtility(IRegistry)
        registry["plone.use_ajax_main_template"] = True
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.request.form["ajax_load"] = False
        self.assertIn("/main_template.pt", self.view.template.filename)

    def test_main_template_no_ajax_2(self):
        """Test a falsy ajax_load value does not lead to ajax_main_template.pt."""
        registry = getUtility(IRegistry)
        registry["plone.use_ajax_main_template"] = True
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.request.form["ajax_load"] = "0"
        self.assertIn("/main_template.pt", self.view.template.filename)

    def test_main_template_no_ajax_3(self):
        """Test a falsy ajax_load value does not lead to ajax_main_template.pt."""
        registry = getUtility(IRegistry)
        registry["plone.use_ajax_main_template"] = True
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.request.form["ajax_load"] = "off"
        self.assertIn("/main_template.pt", self.view.template.filename)
