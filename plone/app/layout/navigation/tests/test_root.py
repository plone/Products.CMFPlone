from plone.app.layout.navigation.root import getNavigationRootObject

from plone.app.testing.bbb import PloneTestCase


class NavigationRootTestCase(PloneTestCase):
    """base test case with convenience methods for all navigation root tests"""

    def test_getNavigationRootObject_no_context(self):
        '''
        If you don't know the context then you also don't know what the
        navigation root is.
        '''
        self.assertEqual(
            None,
            getNavigationRootObject(None, self.portal)
        )
