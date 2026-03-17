from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.users import UnrestrictedUser
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from plone.testing.zope import Browser
from zope.configuration import xmlconfig

import unittest


class PrivateParentErrorMessageLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import Products.CMFPlone

        xmlconfig.file(
            "configure.zcml", Products.CMFPlone, context=configurationContext
        )

    def setUpPloneSite(self, portal):
        user = UnrestrictedUser("manager", "", ["Manager"], "")
        newSecurityManager(None, user.__of__(portal.acl_users))
        try:
            portal.portal_workflow.setDefaultChain("simple_publication_workflow")
            portal.invokeFactory("Folder", id="private-folder", title="Private Folder")
            folder = portal["private-folder"]
            folder.manage_permission("View", roles=["Manager"], acquire=False)
        finally:
            noSecurityManager()


PRIVATE_PARENT_ERROR_MESSAGE_FIXTURE = PrivateParentErrorMessageLayer()

PRIVATE_PARENT_ERROR_MESSAGE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PRIVATE_PARENT_ERROR_MESSAGE_FIXTURE,),
    name="PrivateParentErrorMessageLayer:Functional",
)


class TestPrivateParentErrorMessage(unittest.TestCase):
    layer = PRIVATE_PARENT_ERROR_MESSAGE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = True
        self.browser.raiseHttpErrors = False
        self.browser.addHeader("Accept", "text/html")
        self.browser.open(self.portal.absolute_url())

    def test_404_under_private_parent_includes_css(self):
        self.browser.open(
            f"{self.portal.absolute_url()}/private-folder/non-existing-page"
        )

        self.assertEqual(self.browser.headers["Status"], "404 Not Found")
        self.assertIn("This page does not seem to exist", self.browser.contents)
        self.assertIn("barceloneta.min.css", self.browser.contents)
