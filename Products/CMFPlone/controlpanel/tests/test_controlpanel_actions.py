from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getMultiAdapter
import unittest


class PortalActionsIntegrationTest(unittest.TestCase):
    """Test portal actions control panel."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):  # NOQA
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_actions = getToolByName(self.portal, 'portal_actions')

    def test_actions_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="actions-controlpanel")
        self.assertTrue(view())

    def test_actions_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue('ActionSettings' in [
            a.getAction(self)['id']
            for a in self.controlpanel.listActions()
        ])

    def test_edit_action_controlpanel_view(self):
        action = self.portal_actions.site_actions.sitemap
        view = getMultiAdapter((action, self.portal.REQUEST),
                               name="action-form")
        self.assertTrue(view())

    def test_new_action_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="new-action")
        self.assertTrue(view())
