from DateTime import DateTime
from plone.app.layout.viewlets.content import ContentRelatedItems
from plone.app.layout.viewlets.content import DocumentBylineViewlet
from plone.app.layout.viewlets.content import HistoryByLineView
from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.locking.interfaces import ILockable
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.CMFPlone.interfaces import ISiteSchema
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.interface import Interface
from zope.intid.interfaces import IIntIds

try:
    import pkg_resources
    pkg_resources.get_distribution('plone.app.relationfield')
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY = False
    pass
else:
    HAS_DEXTERITY = True
    from plone.dexterity.fti import DexterityFTI

    class IMyDexterityItem(Interface):
        """ Dexterity test type
        """


class TestDocumentBylineViewletView(ViewletsTestCase):
    """
    Test the document by line viewlet
    """
    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'doc1', title='Document 1')
        self.context = self.folder['doc1']

        registry = getUtility(IRegistry)
        self.security_settings = registry.forInterface(
            ISecuritySchema,
            prefix='plone',
        )

    def _get_viewlet(self):
        request = self.app.REQUEST
        viewlet = DocumentBylineViewlet(self.context, request, None, None)
        viewlet.update()
        return viewlet

    def test_anonymous_locked_icon(self):
        viewlet = self._get_viewlet()
        ILockable(self.context).lock()
        self.logout()
        viewlet = self._get_viewlet()
        self.assertEqual(viewlet.locked_icon(), '')

    def test_locked_icon(self):
        viewlet = self._get_viewlet()
        self.assertEqual(viewlet.locked_icon(), "")
        ILockable(self.context).lock()
        lockIconUrl = (
            '<img src="http://nohost/plone/lock_icon.png" alt="" '
            'title="Locked" height="16" width="16" />'
        )
        self.assertEqual(viewlet.locked_icon(), lockIconUrl)

    def test_pub_date(self):
        # configure our portal to enable publication date on pages globally on
        # the site
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema,
            prefix='plone')

        settings.display_publication_date_in_byline = True

        self.logout()
        viewlet = self._get_viewlet()

        # publication date should be None as there is not Effective date set
        # for our document yet
        self.assertEqual(viewlet.pub_date(), None)

        # now set effective date for our document
        effective = DateTime()
        self.context.setEffectiveDate(effective)
        self.assertEqual(viewlet.pub_date(), DateTime(effective.ISO8601()))

        # now switch off publication date globally on the site and see if
        # viewlet returns None for publication date
        settings.display_publication_date_in_byline = False
        self.assertEqual(viewlet.pub_date(), None)


class TestHistoryBylineViewletView(ViewletsTestCase):
    """
    Test the document by line viewlet
    """
    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'doc1', title='Document 1')
        self.context = self.folder['doc1']

        registry = getUtility(IRegistry)
        self.security_settings = registry.forInterface(
            ISecuritySchema,
            prefix='plone',
        )

    def _get_viewlet(self):
        request = self.app.REQUEST
        viewlet = HistoryByLineView(self.context, request)
        viewlet.update()
        return viewlet

    def test_show_anonymous_not_allowed(self):
        self.security_settings.allow_anon_views_about = False
        self.logout()
        viewlet = self._get_viewlet()
        self.assertFalse(viewlet.show())

    def test_show_anonymous_allowed(self):
        self.security_settings.allow_anon_views_about = True
        self.logout()
        viewlet = self._get_viewlet()
        self.assertTrue(viewlet.show())

    def test_show_logged_in_anonymous_not_allowed(self):
        self.security_settings.allow_anon_views_about = False
        viewlet = self._get_viewlet()
        self.assertTrue(viewlet.show())

    def test_show_logged_in_anonymous_allowed(self):
        self.security_settings.allow_anon_views_about = True
        viewlet = self._get_viewlet()
        self.assertTrue(viewlet.show())

    def test_anonymous_locked_icon_not_locked(self):
        self.logout()
        viewlet = self._get_viewlet()
        self.assertEqual(viewlet.locked_icon(), "")

    def test_anonymous_locked_icon_is_locked(self):
        self.logout()
        ILockable(self.context).lock()
        viewlet = self._get_viewlet()
        self.assertEqual(viewlet.locked_icon(), "")

    def test_logged_in_locked_icon_not_locked(self):
        viewlet = self._get_viewlet()
        self.assertEqual(viewlet.locked_icon(), "")

    def test_logged_in_locked_icon_is_locked(self):
        viewlet = self._get_viewlet()
        ILockable(self.context).lock()
        lockIconUrl = '<img src="http://nohost/plone/lock_icon.png" alt="" \
title="Locked" height="16" width="16" />'
        self.assertEqual(viewlet.locked_icon(), lockIconUrl)

    def test_pub_date(self):
        # configure our portal to enable publication date on pages globally on
        # the site
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema,
            prefix='plone')

        settings.display_publication_date_in_byline = True

        self.logout()
        viewlet = self._get_viewlet()

        # publication date should be None as there is not Effective date set
        # for our document yet
        self.assertEqual(viewlet.pub_date(), None)

        # now set effective date for our document
        effective = DateTime()
        self.context.setEffectiveDate(effective)
        self.assertEqual(viewlet.pub_date(), DateTime(effective.ISO8601()))

        # now switch off publication date globally on the site and see if
        # viewlet returns None for publication date
        settings.display_publication_date_in_byline = False
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
        self.assertEqual([x.Title for x in related], [
                         'Document 2', 'Document 3'])


class TestDexterityRelatedItemsViewlet(ViewletsTestCase):

    def afterSetUp(self):
        """ create some sample content to test with """
        if not HAS_DEXTERITY:
            return
        self.setRoles(('Manager',))
        fti = DexterityFTI('Dexterity Item with relatedItems behavior')
        self.portal.portal_types._setObject(
            'Dexterity Item with relatedItems behavior', fti)
        fti.klass = 'plone.dexterity.content.Item'
        test_module = 'plone.app.layout.viewlets.tests.test_content'
        fti.schema = test_module + '.IMyDexterityItem'
        fti.behaviors = ('plone.app.relationfield.behavior.IRelatedItems',)
        fti = DexterityFTI('Dexterity Item without relatedItems behavior')
        self.portal.portal_types._setObject(
            'Dexterity Item without relatedItems behavior', fti)
        fti.klass = 'plone.dexterity.content.Item'
        fti.schema = test_module + '.IMyDexterityItem'
        self.folder.invokeFactory('Document', 'doc1', title='Document 1')
        self.folder.invokeFactory('Document', 'doc2', title='Document 2')
        self.folder.invokeFactory(
            'Dexterity Item with relatedItems behavior', 'dex1')
        self.folder.invokeFactory(
            'Dexterity Item with relatedItems behavior', 'dex2')
        self.folder.invokeFactory(
            'Dexterity Item without relatedItems behavior', 'dex3')
        self.portal.portal_quickinstaller.installProduct('plone.app.intid')
        intids = getUtility(IIntIds)
        self.folder.dex1.relatedItems = [
            RelationValue(intids.getId(self.folder.doc1)),
            RelationValue(intids.getId(self.folder.doc2)),
        ]

    def testDexterityRelatedItems(self):
        request = self.app.REQUEST
        viewlet = ContentRelatedItems(self.folder.dex1, request, None, None)
        viewlet.update()
        related = viewlet.related_items()
        self.assertEqual([x.id for x in related], ['doc1', 'doc2'])

        # TODO: we should test with non-published objects and anonymous
        #       users but current workflow has no transition to make an
        #       item private

    def testDexterityEmptyRelatedItems(self):
        request = self.app.REQUEST
        viewlet = ContentRelatedItems(self.folder.dex2, request, None, None)
        viewlet.update()
        related = viewlet.related_items()
        self.assertEqual(len(related), 0)

    def testDexterityWithoutRelatedItemsBehavior(self):
        request = self.app.REQUEST
        viewlet = ContentRelatedItems(self.folder.dex2, request, None, None)
        viewlet.update()
        related = viewlet.related_items()
        self.assertEqual(len(related), 0)

    def testDexterityFolderRelatedItems(self):
        """
        Related items viewlet doesn't include related folder's descendants.
        """
        self.assertTrue(
            self.folder.contentValues(), 'Folder is missing descendants')

        intids = getUtility(IIntIds)
        self.folder.dex1.relatedItems = [
            RelationValue(intids.getId(self.folder))]

        request = self.app.REQUEST
        viewlet = ContentRelatedItems(self.folder.dex1, request, None, None)
        viewlet.update()
        related = viewlet.related_items()
        self.assertEqual(len(related), 1)
