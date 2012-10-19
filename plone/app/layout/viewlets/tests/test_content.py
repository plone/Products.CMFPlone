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
        
        # configure our portal and context to get publication date not None
        properties = getToolByName(context, 'portal_properties')
        site_properties = getattr(properties, 'site_properties')
        site_properties.displayPublicationDateInByline = True
        wtool = getToolByName(context, 'portal_workflow')
        wtool.doActionFor(context, 'publish')

        self.login('Ano')
        viewlet = DocumentBylineViewlet(context, request, None, None)
        viewlet.update()
        
        # publication date should be not None now
        self.failIf(viewlet.pub_date() is None)
        
        # now set publication date in workflow history manually
        published = DateTime('2012/03/14')
        context.workflow_history[wtool.getChainFor('Document')[0]][-1]['time'] = \
            published
        # purge instance memoize cache
        delattr(viewlet, Memojito.propname)
        self.assertEqual(viewlet.pub_date(), published)
        
        # set Effective Date and check if it'll be used
        effective = DateTime('2012/03/15')
        context.setEffectiveDate(effective)
        # purge instance memoize cache
        delattr(viewlet, Memojito.propname)
        self.assertEqual(viewlet.pub_date(),
            DateTime(effective.toZone(_zone).ISO8601()))
        
        # now make document private and ensure publication date will return None
        self.login('Alan')
        wtool.doActionFor(context, 'retract')
        self.login('Ano')
        # purge instance memoize cache
        delattr(viewlet, Memojito.propname)
        self.assertEqual(viewlet.pub_date(), None)
        
        # move it back to public
        self.login('Alan')
        wtool.doActionFor(context, 'publish')
        self.login('Ano')
        # purge instance memoize cache
        delattr(viewlet, Memojito.propname)
        self.failIf(viewlet.pub_date() is None)
        
        # and finally check that our global site setting
        # 'Display pub date in byline' works properly
        # purge instance memoize cache
        site_properties.displayPublicationDateInByline = False
        delattr(viewlet, Memojito.propname)
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
