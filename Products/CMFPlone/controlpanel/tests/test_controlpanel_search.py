from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISearchSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
import unittest


class SearchRegistryIntegrationTest(unittest.TestCase):
    """Test that the search settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ISearchSchema, prefix="plone")

    def test_search_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="search-controlpanel")
        self.assertTrue(view())

    def test_search_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue('SearchSettings' in [
            a.getAction(self)['id']
            for a in self.controlpanel.listActions()
        ])

    def test_enable_livesearch_attribute_exists(self):
        self.assertTrue(hasattr(self.settings, 'enable_livesearch'))

    def test_types_not_searched(self):
        self.assertTrue(hasattr(self.settings, 'types_not_searched'))

    def test_sort_on(self):
        self.assertTrue(hasattr(self.settings, 'sort_on'))
