import unittest
from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.app.layout.viewlets.content import DocumentBylineViewlet
from plone.locking.tests import addMember
from plone.locking.interfaces import ILockable

class TestDocumentBylineViewletView(ViewletsTestCase):
    """
    Test the document by line viewlet
    """
    def afterSetUp(self):
        addMember(self, 'Alan', roles=('Member', 'Manager'))
        addMember(self, 'Ano', roles=())

    def test_anonymous_locked_icon(self):
        request = self.app.REQUEST
        self.setRoles(['Manager', 'Member'])
        self.portal.invokeFactory('Document', 'd1')
        context = getattr(self.portal, 'd1')
        viewlet = DocumentBylineViewlet(context, request, None, None)
        viewlet.update()
        ILockable(context).lock()
        self.login('Ano')
        viewlet = DocumentBylineViewlet(context, request, None, None)
        viewlet.update()
        self.assertEqual(viewlet.locked_icon(), "")

    def test_locked_icon(self):
        request = self.app.REQUEST
        self.setRoles(['Manager', 'Member'])
        self.portal.invokeFactory('Document', 'd1')
        context = getattr(self.portal, 'd1')
        viewlet = DocumentBylineViewlet(context, request, None, None)
        viewlet.update()
        self.assertEqual(viewlet.locked_icon(), "")
        ILockable(context).lock()
        self.assertEqual(viewlet.locked_icon(), "")
        self.login('Alan')
        viewlet = DocumentBylineViewlet(context, request, None, None)
        viewlet.update()
        lockIconUrl = '<img src="http://nohost/plone/lock_icon.gif" alt="" \
title="Locked" height="16" width="16" />'
        self.assertEqual(viewlet.locked_icon(), lockIconUrl)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDocumentBylineViewletView))
    return suite
