from plone.registry.interfaces import IRegistry
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class TestMainTemplate(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"].clone()

    def test_request_containment(self):
        """Very basic test to show that the following works:
        `"ajax_load" in request`
        instead of:
        `request.get("ajax_load", MARKER) is not MARKER1`
        """
        self.request.form["ajax_load"] = True
        self.assertTrue("ajax_load" in self.request.form)
        self.assertTrue("ajax_load" in self.request)

    def test_main_template_standard(self):
        """Test the standard case to use the main_template.pt."""
        view = getMultiAdapter((self.portal, self.request), name="main_template")
        self.assertIn("/main_template.pt", view.template.filename)

    def test_main_template_ajax_parameter(self):
        """Test, if an explicitly set `ajax_load` URL parameter leads to use
        the ajax_main_template.pt.
        """
        self.request.form["ajax_load"] = True
        view = getMultiAdapter((self.portal, self.request), name="main_template")
        self.assertIn("/ajax_main_template.pt", view.template.filename)

    def test_main_template_ajax_manually(self):
        """Test, if an explicitly set `ajax_load` request parameter leads to
        use the ajax_main_template.pt.
        """
        self.request.set("ajax_load", True)
        view = getMultiAdapter((self.portal, self.request), name="main_template")
        self.assertIn("/ajax_main_template.pt", view.template.filename)

    def test_main_template_auto(self):
        """Test, if an AJAX request leads to the ajax_main_template.pt."""
        registry = getUtility(IRegistry)
        registry["plone.use_ajax"] = True
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        view = getMultiAdapter((self.portal, self.request), name="main_template")
        self.assertIn("/ajax_main_template.pt", view.template.filename)

    def test_main_template_noauto_if_set(self):
        """Test a falsy ajax_load value and a AJAX request forces to use the
        normal main_template and not the ajax_main_template.pt.
        """
        registry = getUtility(IRegistry)
        registry["plone.use_ajax"] = True
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.request.form["ajax_load"] = "False"
        view = getMultiAdapter((self.portal, self.request), name="main_template")
        self.assertIn("/main_template.pt", view.template.filename)

    def test_main_template_no_ajax_1(self):
        """Test a falsy ajax_load value does not lead to ajax_main_template.pt."""
        registry = getUtility(IRegistry)
        registry["plone.use_ajax"] = True
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.request.form["ajax_load"] = False
        view = getMultiAdapter((self.portal, self.request), name="main_template")
        self.assertIn("/main_template.pt", view.template.filename)

    def test_main_template_no_ajax_2(self):
        """Test a falsy ajax_load value does not lead to ajax_main_template.pt."""
        registry = getUtility(IRegistry)
        registry["plone.use_ajax"] = True
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.request.form["ajax_load"] = "0"
        view = getMultiAdapter((self.portal, self.request), name="main_template")
        self.assertIn("/main_template.pt", view.template.filename)

    def test_main_template_no_ajax_3(self):
        """Test a falsy ajax_load value does not lead to ajax_main_template.pt."""
        registry = getUtility(IRegistry)
        registry["plone.use_ajax"] = True
        self.request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.request.form["ajax_load"] = "off"
        view = getMultiAdapter((self.portal, self.request), name="main_template")
        self.assertIn("/main_template.pt", view.template.filename)
