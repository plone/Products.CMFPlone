from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter

import transaction
import unittest


class SyndicationControlPanelFunctionalTest(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        )

    def test_syndication_controlpanel_link(self):
        self.browser.open("%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink("Syndication").click()

    def test_syndication_controlpanel_backlink(self):
        self.browser.open("%s/@@syndication-controlpanel" % self.portal_url)
        self.assertTrue("General" in self.browser.contents)

    def test_syndication_controlpanel_sidebar(self):
        self.browser.open("%s/@@syndication-controlpanel" % self.portal_url)
        self.browser.getLink("Site Setup").click()
        self.assertTrue(self.browser.url.endswith("/plone/@@overview-controlpanel"))

    def test_syndication_controlpanel_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="syndication-controlpanel"
        )
        self.assertTrue(view())

    def test_syndication_controlpanel_enabled(self):
        self.browser.open("%s/@@syndication-controlpanel" % self.portal_url)
        self.browser.getControl(name="form.widgets.default_enabled:list").value = True
        self.browser.getControl(name="form.widgets.show_author_info:list").value = False
        self.browser.getControl(
            name="form.widgets.show_syndication_link:list"
        ).value = True
        self.browser.getControl("Save").click()

        self.assertTrue("Changes saved" in self.browser.contents)
        self.browser.open("%s/@@syndication-controlpanel" % self.portal_url)

        self.assertEqual(
            self.browser.getControl(name="form.widgets.default_enabled:list").value,
            ["selected"],
        )
        self.assertEqual(
            self.browser.getControl(name="form.widgets.show_author_info:list").value, []
        )
        self.assertEqual(
            self.browser.getControl(
                name="form.widgets.show_syndication_link:list"
            ).value,
            ["selected"],
        )

    def test_create_collection(self):
        """Create collection and check if synPropertiesForm link is present."""
        # create collection
        self.portal.invokeFactory("Collection", "collection")
        self.portal.collection.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.any",
                "v": ["News Item"],
            },
            {
                "i": "review_state",
                "o": "plone.app.querystring.operation.selection.any",
                "v": ["published"],
            },
        ]
        transaction.commit()
        # Enable syndication
        self.browser.open("%s/@@syndication-controlpanel" % self.portal_url)
        self.browser.getControl(name="form.widgets.default_enabled:list").value = [
            "selected"
        ]
        self.browser.getControl(
            name="form.widgets.show_syndication_link:list"
        ).value = ["selected"]
        self.browser.getControl("Save").click()
        self.assertTrue("Changes saved" in self.browser.contents)

        self.browser.open(self.portal_url + "/collection")
        self.assertTrue("/RSS" in self.browser.contents)
