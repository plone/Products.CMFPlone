from zope.component import getMultiAdapter
from zope.component import getSiteManager

from plone.portlets.interfaces import IPortletManager

from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.portlets.config import PORTLETMANAGER_FOLDER

class TestProductInstall(PortletsTestCase):

    def testPortletManagersInstalled(self):
        self.failUnless(PORTLETMANAGER_FOLDER in self.portal.objectIds())
        portlets = self.portal[PORTLETMANAGER_FOLDER]
        
        self.failUnless('left' in portlets.objectIds())
        self.failUnless('right' in portlets.objectIds())
        self.failUnless('dashboard' in portlets.objectIds())
        
    def testPortletManagersRegistered(self):
        sm = getSiteManager(self.portal)
        registrations = [r.name for r in sm.registeredAdapters()
                            if IPortletManager.providedBy(r.factory)]
        registrations.sort()
        
        self.assertEquals(['plone.dashboard', 'plone.leftcolumn', 'plone.rightcolumn'], registrations)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
