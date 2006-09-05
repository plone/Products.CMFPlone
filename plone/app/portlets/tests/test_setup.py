from zope.app.component.hooks import setSite, setHooks
from zope.component import getSiteManager, getUtilitiesFor

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletType

from plone.app.portlets.tests.base import PortletsTestCase

class TestProductInstall(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def testPortletManagersRegistered(self):
        sm = getSiteManager(self.portal)
        registrations = [r.name for r in sm.registeredUtilities()
                            if IPortletManager == r.provided]
        self.assertEquals(['plone.dashboard', 'plone.leftcolumn', 'plone.rightcolumn'], sorted(registrations))
        
    def testAssignable(self):
        self.failUnless(ILocalPortletAssignable.providedBy(self.folder))
        self.failUnless(ILocalPortletAssignable.providedBy(self.portal))
        
    def testPortletTypesRegistered(self): 
        portlets = [u[0] for u in getUtilitiesFor(IPortletType)]
        self.failUnless('portlets.Classic' in portlets)
        self.failUnless('portlets.Login' in portlets)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
