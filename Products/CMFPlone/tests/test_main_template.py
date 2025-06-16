from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.event import notify
from zope.traversing.interfaces import BeforeTraverseEvent

import unittest


class TestMainTemplate(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_request_containment(self):
        """Very basic test to show that the following works:
        `"ajax_load" in request`
        instead of:
        `request.get("ajax_load", MARKER) is not MARKER1`
        """
        request = self.request.clone()
        request.form["ajax_load"] = True
        self.assertTrue("ajax_load" in request.form)
        self.assertTrue("ajax_load" in request)

    def test_main_template_standard(self):
        view = getMultiAdapter((self.portal, self.request), name="main_template")
        self.assertEqual(view.template_name, "templates/main_template.pt")

    def test_main_template_ajax_parameter(self):
        request = self.request.clone()
        request.form["ajax_load"] = True
        view = getMultiAdapter((self.portal, request), name="main_template")
        self.assertEqual(view.template_name, "templates/ajax_main_template.pt")

    def test_main_template_ajax_manually(self):
        request = self.request.clone()
        request.set("ajax_load", True)
        view = getMultiAdapter((self.portal, request), name="main_template")
        self.assertEqual(view.template_name, "templates/ajax_main_template.pt")

    def test_main_template_auto(self):
        request = self.request.clone()
        request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        # Manually trigger the BeforeTraverseEvent to set the ajax_load
        # parameter - using restrictedTraverse would not work here
        notify(BeforeTraverseEvent(self.portal, request))
        view = getMultiAdapter((self.portal, request), name="main_template")
        self.assertEqual(view.template_name, "templates/ajax_main_template.pt")

    def test_main_template_noauto_if_set(self):
        request = self.request.clone()
        request.form["ajax_load"] = "False"
        request.environ["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        # Manually trigger the BeforeTraverseEvent to set the ajax_load
        # parameter - using restrictedTraverse would not work here
        notify(BeforeTraverseEvent(self.portal, request))
        view = getMultiAdapter((self.portal, request), name="main_template")
        self.assertEqual(view.template_name, "templates/main_template.pt")

    def test_main_template_no_ajax_1(self):
        request = self.request.clone()
        request.form["ajax_load"] = False
        view = getMultiAdapter((self.portal, request), name="main_template")
        self.assertEqual(view.template_name, "templates/main_template.pt")

    def test_main_template_no_ajax_2(self):
        request = self.request.clone()
        request.form["ajax_load"] = "0"
        view = getMultiAdapter((self.portal, request), name="main_template")
        self.assertEqual(view.template_name, "templates/main_template.pt")

    def test_main_template_no_ajax_3(self):
        request = self.request.clone()
        request.form["ajax_load"] = "off"
        view = getMultiAdapter((self.portal, request), name="main_template")
        self.assertEqual(view.template_name, "templates/main_template.pt")
