from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import Browser

import lxml
import transaction
import unittest


class ProductsCMFPloneSetupTest(unittest.TestCase):
    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()

        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        )
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_sitemap(self):
        self.portal.invokeFactory("Document", "doc1", title="Document 1")
        self.portal.invokeFactory("Document", "doc2", title="Document 2")
        self.portal.invokeFactory("Document", "doc3", title="Document 3")
        transaction.commit()
        self.browser.open(self.portal_url + "/sitemap")
        output = lxml.html.fromstring(self.browser.contents)
        sitemap = output.xpath("//ul[@id='portal-sitemap']")[0].text_content()

        self.assertTrue("Document 1" in sitemap)
        self.assertTrue("Document 2" in sitemap)
        self.assertTrue("Document 3" in sitemap)

    def test_sitemap_nested(self):
        self.portal.invokeFactory("Folder", "folder1", title="Folder 1")
        self.portal.invokeFactory("Document", "doc1", title="Document 1")
        self.portal.invokeFactory("Folder", "folder2", title="Folder 2")
        self.portal.folder1.invokeFactory("Document", "doc12", title="Document 12")
        transaction.commit()

        self.browser.open(self.portal_url + "/sitemap")
        output = lxml.html.fromstring(self.browser.contents)
        sitemap = output.xpath("//ul[@id='portal-sitemap']")[0].text_content()

        self.assertTrue("Folder 1" in sitemap)
        self.assertTrue("Document 1" in sitemap)
        self.assertTrue("Folder 2" in sitemap)
        self.assertTrue("Document 12" in sitemap)
