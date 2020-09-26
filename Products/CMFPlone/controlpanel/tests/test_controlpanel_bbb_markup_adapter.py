from Products.CMFPlone.interfaces import IMarkupSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import unittest
from plone.app.testing import TEST_USER_ID, setRoles
from zope.component import getAdapter


class MarkupControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IMarkupSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, IMarkupSchema))

    def test_get_default_type(self):
        self.settings.default_type = 'text/plain'
        self.assertEqual(
            getAdapter(self.portal, IMarkupSchema).default_type,
            'text/plain'
        )

    def test_set_default_type(self):
        getAdapter(self.portal, IMarkupSchema).default_type = 'text/plain'  # noqa
        self.assertEqual(
            self.settings.default_type,
            'text/plain'
        )

    def test_get_allowed_types(self):
        self.settings.allowed_types = ('text/plain', 'text/x-web-textile')
        self.assertEqual(
            getAdapter(self.portal, IMarkupSchema).allowed_types,
            ('text/plain', 'text/x-web-textile')
        )

    def test_set_allowed_types(self):
        getAdapter(self.portal, IMarkupSchema).allowed_types =\
            ('text/plain', 'text/x-web-textile')
        self.assertEqual(
            self.settings.allowed_types,
            ('text/plain', 'text/x-web-textile')
        )
