from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase


class TestAccessControlPanelScripts(PloneTestCase):
    """Yipee, functional tests"""

    def afterSetUp(self):
        self.portal_path = self.portal.absolute_url(1)
        self.basic_auth = f"{SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"

    def testUserInformation(self):
        """Test access to user details."""
        response = self.publish(
            f"{self.portal_path}/@@user-information?userid={TEST_USER_ID}",
            self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 200)

    def testUserPreferences(self):
        """Test access to user details."""
        response = self.publish(
            f"{self.portal_path}/@@user-preferences?userid={TEST_USER_ID}",
            self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 200)
