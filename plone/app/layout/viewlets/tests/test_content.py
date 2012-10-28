from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.app.layout.viewlets.content import DocumentBylineViewlet
from plone.app.layout.viewlets.content import ContentRelatedItems
from plone.locking.tests import addMember
from plone.locking.interfaces import ILockable
from plone.memoize.instance import Memojito

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.ExtensibleMetadata import _zone


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
        lockIconUrl = '<img src="http://nohost/plone/lock_icon.png" alt="" \
title="Locked" height="16" width="16" />'
        self.assertEqual(viewlet.locked_icon(), lockIconUrl)
    
    def test_pub_date(self):
        request = self.app.REQUEST
        self.login('Alan')
        self.portal.invokeFactory('Document', 'd1')
        context = getattr(self.portal, 'd1')
        
        # configure our portal to enable publication date on pages globally on
        # the site
        properties = getToolByName(context, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        site_properties.displayPublicationDateInByline = True

        self.login('Ano')
        viewlet = DocumentBylineViewlet(context, request, None, None)
        viewlet.update()
        
        # publication date should be None as there is not Effective date set for
        # our document yet
        self.assertEqual(viewlet.pub_date(), None)

        # now set effective date for our document
        effective = DateTime()
        context.setEffectiveDate(effective)
        self.assertEqual(viewlet.pub_date(), DateTime(effective.ISO8601()))
        
        # now switch off publication date globally on the site and see if
        # viewlet returns None for publication date
        site_properties.displayPublicationDateInByline = False
        self.assertEqual(viewlet.pub_date(), None)

class TestRelatedItemsViewlet(ViewletsTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'doc1', title='Document 1')
        self.folder.invokeFactory('Document', 'doc2', title='Document 2')
        self.folder.invokeFactory('Document', 'doc3', title='Document 3')
        self.folder.doc1.setRelatedItems([self.folder.doc2, self.folder.doc3])

    def testRelatedItems(self):
        request = self.app.REQUEST
        viewlet = ContentRelatedItems(self.folder.doc1, request, None, None)
        viewlet.update()
        related = viewlet.related_items()
        self.assertEqual([x.Title for x in related], ['Document 2', 'Document 3'])


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
