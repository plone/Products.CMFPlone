import unittest
from zope import interface
from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.navigation.interfaces import INavigationRoot

class TestViewletBase(ViewletsTestCase):
    """
    Test the base class for the viewlets
    """
    def test_update(self):
        request = self.app.REQUEST
        self.setRoles(['Manager', 'Member'])
        self.portal.invokeFactory('Folder', 'f1')
        context = getattr(self.portal, 'f1')
        interface.alsoProvides(context, INavigationRoot)
        viewlet = ViewletBase(context, request, None, None)
        viewlet.update()
        self.assertEqual(viewlet.site_url, "http://nohost/plone")
        self.assertEqual(viewlet.navigation_root_url, "http://nohost/plone/f1")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestViewletBase))
    return suite
