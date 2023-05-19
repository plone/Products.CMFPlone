from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.base.interfaces import INavigationSchema
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class NavigationControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the navigation control panel are actually
    stored in the registry.
    """

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

    def test_navigation_control_panel_link(self):
        self.browser.open("%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink("Navigation").click()
        self.assertTrue("Navigation Settings" in self.browser.contents)

    def test_navigation_control_panel_backlink(self):
        self.browser.open("%s/@@navigation-controlpanel" % self.portal_url)
        self.assertTrue("General" in self.browser.contents)

    def test_navigation_control_panel_sidebar(self):
        self.browser.open("%s/@@navigation-controlpanel" % self.portal_url)
        self.browser.getLink("Site Setup").click()
        self.assertTrue(self.browser.url.endswith("/plone/@@overview-controlpanel"))

    def test_navigation_controlpanel_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="navigation-controlpanel"
        )
        self.assertTrue(view())

    def test_generate_tabs(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        self.browser.open("%s/@@navigation-controlpanel" % self.portal_url)
        self.assertEqual(settings.generate_tabs, True)
        self.assertEqual(
            self.browser.getControl("Automatically generate tabs").selected, True
        )
        self.browser.getControl("Automatically generate tabs").selected = False
        self.browser.getControl("Save").click()

        self.assertEqual(settings.generate_tabs, False)

    def test_nonfolderish_tabs(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        self.browser.open("%s/@@navigation-controlpanel" % self.portal_url)
        self.assertEqual(settings.generate_tabs, True)
        self.assertEqual(
            self.browser.getControl("Automatically generate tabs").selected, True
        )
        self.browser.getControl(
            "Generate tabs for items other than folders"
        ).selected = False
        self.browser.getControl("Save").click()

        self.assertEqual(settings.nonfolderish_tabs, False)

    def test_displayed_types(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        self.browser.open("%s/@@navigation-controlpanel" % self.portal_url)
        self.browser.getControl("Collection", index=0).selected = True
        self.browser.getControl("Comment").selected = True
        self.browser.getControl("Event").selected = True
        self.browser.getControl("File").selected = True
        self.browser.getControl("Folder").selected = True
        self.browser.getControl("Image").selected = True
        self.browser.getControl("Link").selected = True
        self.browser.getControl("News Item").selected = True
        self.browser.getControl("Page").selected = True
        self.browser.getControl("Save").click()

        self.assertTrue("Collection" in settings.displayed_types)
        self.assertTrue("Discussion Item" in settings.displayed_types)
        self.assertTrue("Event" in settings.displayed_types)
        self.assertTrue("File" in settings.displayed_types)
        self.assertTrue("Folder" in settings.displayed_types)
        self.assertTrue("Image" in settings.displayed_types)
        self.assertTrue("Link" in settings.displayed_types)
        self.assertTrue("News Item" in settings.displayed_types)
        self.assertTrue("Document" in settings.displayed_types)

    def test_workflow_settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        self.browser.open("%s/@@navigation-controlpanel" % self.portal_url)

        self.browser.getControl("Filter on workflow state").selected = True
        self.browser.getControl("Externally visible [external]").selected = True  # noqa
        self.browser.getControl("Internal draft [internal]").selected = True
        self.browser.getControl(
            "Internally published [internally_published]"
        ).selected = True  # noqa
        self.browser.getControl("Pending [pending]").selected = True
        self.browser.getControl("Private [private]").selected = True
        self.browser.getControl("Public draft [visible]").selected = True
        self.browser.getControl("Published [published]").selected = True
        self.browser.getControl("Save").click()

        self.assertTrue(self.browser.url.endswith("navigation-controlpanel"))
        self.assertTrue("Changes saved." in self.browser.contents)

        self.assertTrue(settings.filter_on_workflow)

        self.assertTrue("external" in settings.workflow_states_to_show)
        self.assertTrue("internal" in settings.workflow_states_to_show)
        self.assertTrue(
            "internally_published" in settings.workflow_states_to_show
        )  # noqa
        self.assertTrue("pending" in settings.workflow_states_to_show)
        self.assertTrue("private" in settings.workflow_states_to_show)
        self.assertTrue("visible" in settings.workflow_states_to_show)
        self.assertTrue("published" in settings.workflow_states_to_show)

    def test_show_excluded_items(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        self.browser.open("%s/@@navigation-controlpanel" % self.portal_url)

        self.browser.getControl(
            "Show items normally excluded from navigation if viewing their children."
        ).selected = False  # noqa
        self.browser.getControl("Save").click()

        self.assertFalse(settings.show_excluded_items)
