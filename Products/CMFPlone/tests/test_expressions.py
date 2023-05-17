from AccessControl.class_init import InitializeClass
from AccessControl.Permissions import view_management_screens
from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

# Expressions.boboAwareZopeTraverse is a function
# expression(s).BoboAwareZopeTraverse is a class
# Import them with names that are easier to tell apart.
from Products.PageTemplates.expression import BoboAwareZopeTraverse as TraverseClass
from Products.PageTemplates.expression import (
    TrustedBoboAwareZopeTraverse as TrustedTraverseClass,
)
from Products.PageTemplates.Expressions import (
    boboAwareZopeTraverse as traverse_function,
)
from Products.PageTemplates.Expressions import (
    trustedBoboAwareZopeTraverse as trusted_traverse_function,
)
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zExceptions import NotFound
from zExceptions import Unauthorized

import AccessControl
import os
import random
import re
import string
import sys
import unittest


# Path of this directory:
path = os.path.dirname(__file__)


class DummyView:
    __name__ = "dummy-view"
    _authenticator = "secret"
    _ = "translation"
    # Even via weird names, some items should not be reachable:
    os_hack = os
    sys_hack = sys
    Formatter_hack = string.Formatter


class DummyContent(SimpleItem):
    """Dummy content class to show the (un)restrictedTraverse works."""

    security = ClassSecurityInfo()

    @security.public
    def public(self):
        """Public method"""
        return "I am public"

    @security.private
    def private(self):
        """Private method"""
        return "I am private"

    @security.protected(view_management_screens)
    def protected(self):
        """Protected method"""
        return "I am protected"


InitializeClass(DummyContent)


class TestAttackVector(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def _makeOne(self, name):
        return PageTemplateFile(os.path.join(path, name)).__of__(self.layer["portal"])

    def test_template_bad1(self):
        template = self._makeOne("bad1.pt")
        # In some versions, random is not globally available, so we get a NameError.
        # Otherwise our patch should make sure we get a NotFound.
        with self.assertRaises((NotFound, NameError)):
            template()

    def test_template_bad2(self):
        template = self._makeOne("bad2.pt")
        with self.assertRaises(NotFound):
            template()

    def test_template_bad3(self):
        template = self._makeOne("bad3.pt")
        with self.assertRaises(NotFound):
            template()

    def test_template_single_underscore(self):
        # Allow accessing '_' in a skin template or TTW template.
        # In the merge of the hotfix, Zope allows this, to avoid a test failure.
        template = self._makeOne("options_underscore.pt")
        # Pass view in the options.
        self.assertIn("translation", template(view=DummyView()))

    def test_browser_template_with_name(self):
        # Allow accessing __name__ in a browser view template.
        browser = Browser(self.layer["app"])
        browser.handleErrors = False
        browser.open(self.layer["portal"].absolute_url() + "/hotfix-testing-view-name")
        self.assertIn("<h1>hotfix-testing-view-name</h1>", browser.contents)

    def test_template_accesscontrol_sm(self):
        # Only AccessControl.getSecurityManager is allowed.
        template = self._makeOne("accesscontrol_sm.pt")
        self.assertIn("getSecurityManager is allowed", template())

    def test_template_accesscontrol_direct(self):
        # Via AccessControl you can access too much.
        template = self._makeOne("accesscontrol_direct.pt")
        with self.assertRaises(NotFound):
            template()

    def test_template_accesscontrol_via_modules(self):
        template = self._makeOne("accesscontrol_via_modules.pt")
        with self.assertRaises(NotFound):
            template()

    def test_template_accesscontrol_via_dict(self):
        template = self._makeOne("accesscontrol_via_dict.pt")
        with self.assertRaises(NotFound):
            template()


class TestDirectAttackVector(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def test_traverse_function_random(self):
        with self.assertRaises(NotFound):
            traverse_function(random, ("_os", "system"), None)
        # trusted traverse should work fine
        result = trusted_traverse_function(random, ("_os", "system"), None)
        self.assertEqual(result, os.system)

    def test_traverse_function_string(self):
        with self.assertRaises(NotFound):
            traverse_function(string, ("_re", "purge"), None)
        result = trusted_traverse_function(string, ("_re", "purge"), None)
        self.assertEqual(result, re.purge)

    def test_traverse_function_formatter(self):
        with self.assertRaises(NotFound):
            traverse_function(string, ("Formatter",), None)
        result = trusted_traverse_function(string, ("Formatter",), None)
        self.assertEqual(result, string.Formatter)

    def test_traverse_function_formatter_get_field(self):
        with self.assertRaises(NotFound):
            traverse_function(string, ("Formatter", "get_field"), None)
        result = trusted_traverse_function(string, ("Formatter", "get_field"), None)
        self.assertEqual(result, string.Formatter.get_field)

    def test_traverse_function_hacked_names(self):
        view = DummyView()
        with self.assertRaises(NotFound):
            traverse_function(view, ("os_hack",), None)
        with self.assertRaises(NotFound):
            traverse_function(view, ("sys_hack",), None)
        with self.assertRaises(NotFound):
            traverse_function(view, ("Formatter_hack",), None)
        result = trusted_traverse_function(view, ("os_hack",), None)
        self.assertEqual(result, os)
        result = trusted_traverse_function(view, ("sys_hack",), None)
        self.assertEqual(result, sys)
        result = trusted_traverse_function(view, ("Formatter_hack",), None)
        self.assertEqual(result, string.Formatter)

    def test_traverse_function_single_underscore(self):
        # We allow access to '_' always as a special case.
        view = DummyView()
        self.assertEqual(traverse_function(view, ("_",), None), "translation")
        self.assertEqual(trusted_traverse_function(view, ("_",), None), "translation")

    def test_traverse_function_content(self):
        content = DummyContent("dummy")
        self.assertEqual(traverse_function(content, ("public",), None)(), "I am public")
        with self.assertRaises(Unauthorized):
            traverse_function(content, ("private",), None)
        with self.assertRaises(Unauthorized):
            traverse_function(content, ("protected",), None)

        self.assertEqual(
            trusted_traverse_function(content, ("public",), None)(), "I am public"
        )
        self.assertEqual(
            trusted_traverse_function(content, ("private",), None)(), "I am private"
        )
        self.assertEqual(
            trusted_traverse_function(content, ("protected",), None)(), "I am protected"
        )

    def test_traverse_function_accesscontrol_getSecurityManager(self):
        # Only getSecurityManager is allowed.
        self.assertEqual(
            traverse_function(AccessControl, ("getSecurityManager",), None),
            AccessControl.getSecurityManager,
        )
        self.assertEqual(
            trusted_traverse_function(AccessControl, ("getSecurityManager",), None),
            AccessControl.getSecurityManager,
        )

    def test_traverse_function_accesscontrol_direct(self):
        with self.assertRaises(NotFound):
            traverse_function(AccessControl, ("SecurityManagement",), None)
        self.assertEqual(
            trusted_traverse_function(AccessControl, ("SecurityManagement",), None),
            AccessControl.SecurityManagement,
        )

    def test_traverse_function_accesscontrol_via_modules(self):
        from Products.PageTemplates.ZRPythonExpr import _SecureModuleImporter

        modules = _SecureModuleImporter()
        with self.assertRaises(NotFound):
            traverse_function(modules, ("AccessControl", "users"), None)
        self.assertEqual(
            trusted_traverse_function(modules, ("AccessControl", "users"), None),
            AccessControl.users,
        )

    def test_traverse_function_accesscontrol_via_dict(self):
        piggyback = {"unsafe": AccessControl}
        with self.assertRaises(NotFound):
            traverse_function(piggyback, ("unsafe", "users"), None)
        self.assertEqual(
            trusted_traverse_function(piggyback, ("unsafe", "users"), None),
            AccessControl.users,
        )

    def test_traverse_class_random(self):
        with self.assertRaises(NotFound):
            # Note: here the second argument is the request.  None works in the tests.
            TraverseClass.traverse(random, None, ("_os", "system"))
        # trusted traverse should work fine
        result = TrustedTraverseClass.traverse(random, None, ("_os", "system"))
        self.assertEqual(result, os.system)

    def test_traverse_class_string(self):
        with self.assertRaises(NotFound):
            TraverseClass.traverse(string, None, ("_re", "purge"))
        result = TrustedTraverseClass.traverse(string, None, ("_re", "purge"))
        self.assertEqual(result, re.purge)

    def test_traverse_class_formatter(self):
        with self.assertRaises(NotFound):
            TraverseClass.traverse(string, None, ("Formatter",))
        result = TrustedTraverseClass.traverse(string, None, ("Formatter",))
        self.assertEqual(result, string.Formatter)

    def test_traverse_class_formatter_get_field(self):
        with self.assertRaises(NotFound):
            TraverseClass.traverse(string, None, ("Formatter", "get_field"))
        result = TrustedTraverseClass.traverse(string, None, ("Formatter", "get_field"))
        self.assertEqual(result, string.Formatter.get_field)

    def test_traverse_class_content(self):
        content = DummyContent("dummy")
        self.assertEqual(
            TraverseClass.traverse(content, None, ("public",))(), "I am public"
        )
        with self.assertRaises(Unauthorized):
            TraverseClass.traverse(content, None, ("private",))
        with self.assertRaises(Unauthorized):
            TraverseClass.traverse(content, None, ("protected",))

        self.assertEqual(
            TrustedTraverseClass.traverse(content, None, ("public",))(), "I am public"
        )
        self.assertEqual(
            TrustedTraverseClass.traverse(content, None, ("private",))(), "I am private"
        )
        self.assertEqual(
            TrustedTraverseClass.traverse(content, None, ("protected",))(),
            "I am protected",
        )

    def test_traverse_class_accesscontrol_getSecurityManager(self):
        # AccessControl.getSecurityManager is the only item allowed.
        self.assertEqual(
            TraverseClass.traverse(AccessControl, None, ("getSecurityManager",)),
            AccessControl.getSecurityManager,
        )
        self.assertEqual(
            TrustedTraverseClass.traverse(AccessControl, None, ("getSecurityManager",)),
            AccessControl.getSecurityManager,
        )

    def test_traverse_class_accesscontrol_direct(self):
        with self.assertRaises(NotFound):
            TraverseClass.traverse(AccessControl, None, ("SecurityManagement",))
        self.assertEqual(
            TrustedTraverseClass.traverse(AccessControl, None, ("SecurityManagement",)),
            AccessControl.SecurityManagement,
        )

    def test_traverse_class_accesscontrol_via_modules(self):
        from Products.PageTemplates.ZRPythonExpr import _SecureModuleImporter

        modules = _SecureModuleImporter()
        with self.assertRaises(NotFound):
            TraverseClass.traverse(modules, None, ("AccessControl", "users"))
        self.assertEqual(
            TrustedTraverseClass.traverse(modules, None, ("AccessControl", "users")),
            AccessControl.users,
        )

    def test_traverse_class_accesscontrol_via_dict(self):
        piggyback = {"unsafe": AccessControl}
        with self.assertRaises(NotFound):
            TraverseClass.traverse(piggyback, None, ("unsafe", "users"))
        self.assertEqual(
            TrustedTraverseClass.traverse(piggyback, None, ("unsafe", "users")),
            AccessControl.users,
        )
