from Products.CMFPlone.interfaces import INavigationSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getAdapter
from zope.component import getUtility
import unittest


class NavigationControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.navigation_settings = registry.forInterface(
            INavigationSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, INavigationSchema))

    def test_get_generate_tabs(self):
        self.assertEqual(
            getAdapter(self.portal, INavigationSchema).generate_tabs,
            True
        )
        self.navigation_settings.generate_tabs = False
        self.assertEqual(
            getAdapter(self.portal, INavigationSchema).generate_tabs,
            False
        )

    def test_set_generate_tabs(self):
        self.assertEqual(
            self.navigation_settings.generate_tabs,
            True
        )
        getAdapter(self.portal, INavigationSchema).generate_tabs = False
        self.assertEqual(
            self.navigation_settings.generate_tabs,
            False
        )

    def test_get_nonfolderish_tabs(self):
        self.assertEqual(
            getAdapter(self.portal, INavigationSchema).nonfolderish_tabs,
            True
        )
        self.navigation_settings.nonfolderish_tabs = False
        self.assertEqual(
            getAdapter(self.portal, INavigationSchema).nonfolderish_tabs,
            False
        )

    def test_set_nonfolderish_tabs(self):
        self.assertEqual(
            self.navigation_settings.nonfolderish_tabs,
            True
        )
        getAdapter(self.portal, INavigationSchema).nonfolderish_tabs = False
        self.assertEqual(
            self.navigation_settings.nonfolderish_tabs,
            False
        )

    def test_get_displayed_types(self):
        self.navigation_settings.displayed_types = ('Folder',)
        self.assertEqual(
            getAdapter(self.portal, INavigationSchema).displayed_types,
            ('Folder',)
        )

    def test_set_displayed_types(self):
        getAdapter(
            self.portal,
            INavigationSchema
        ).displayed_types = ('Folder',)
        self.assertEqual(
            self.navigation_settings.displayed_types,
            ('Folder',)
        )

    def test_get_filter_on_workflow(self):
        self.assertEqual(
            getAdapter(self.portal, INavigationSchema).filter_on_workflow,
            False
        )
        self.navigation_settings.filter_on_workflow = True
        self.assertEqual(
            getAdapter(self.portal, INavigationSchema).filter_on_workflow,
            True
        )

    def test_set_filter_on_workflow(self):
        self.assertEqual(
            self.navigation_settings.filter_on_workflow,
            False
        )
        getAdapter(self.portal, INavigationSchema).filter_on_workflow = True
        self.assertEqual(
            self.navigation_settings.filter_on_workflow,
            True
        )

    def test_get_workflow_states_to_show(self):
        self.assertEqual(
            getAdapter(self.portal, INavigationSchema).workflow_states_to_show,
            ()
        )

        self.navigation_settings.workflow_states_to_show = ('private',)
        self.assertEqual(
            getAdapter(self.portal, INavigationSchema).workflow_states_to_show,
            ('private',)
        )

    def test_set_workflow_states_to_show(self):
        self.assertEqual(
            self.navigation_settings.workflow_states_to_show,
            ()
        )
        getAdapter(
            self.portal,
            INavigationSchema
        ).workflow_states_to_show = ('private',)
        self.assertEqual(
            self.navigation_settings.workflow_states_to_show,
            ('private',)
        )

    def test_get_show_excluded_items(self):
        self.assertEqual(
            getAdapter(self.portal, INavigationSchema).show_excluded_items,
            False
        )
        self.navigation_settings.show_excluded_items = True
        self.assertEqual(
            getAdapter(self.portal, INavigationSchema).show_excluded_items,
            True
        )

    def test_set_show_excluded_items(self):
        self.assertEqual(
            self.navigation_settings.show_excluded_items,
            False
        )
        getAdapter(self.portal, INavigationSchema).show_excluded_items = True
        self.assertEqual(
            self.navigation_settings.show_excluded_items,
            True
        )
