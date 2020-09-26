from AccessControl import Unauthorized
from Acquisition import aq_base
from OFS.CopySupport import CopyError
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from Products.CMFCore.interfaces import IContentish
from zope.component import provideHandler, getGlobalSiteManager
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from urllib.error import HTTPError

import transaction




class TestCutPasteSecurity(PloneTestCase):

    def afterSetUp(self):
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('user2', 'secret', ['Member'], [])
        self.membership = self.portal.portal_membership
        self.createMemberarea('user1')
        self.createMemberarea('user2')

    def testRenameMemberContent(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='testrename')

        # We need to commit here so that _p_jar isn't None and move
        # will work
        transaction.savepoint(optimistic=True)
        folder.manage_renameObject('testrename', 'new')
        self.assertFalse(hasattr(aq_base(folder), 'testrename'))
        self.assertTrue(hasattr(aq_base(folder), 'new'))

    def testRenameOtherMemberContentFails(self):
        self.login('user1')
        src = self.membership.getHomeFolder('user1')
        src.invokeFactory('Document', id='testrename')

        self.login('user2')
        folder = self.membership.getHomeFolder('user1')
        with self.assertRaises(CopyError):
            folder.manage_renameObject('testrename', 'bad')

    def testCopyMemberContent(self):
        self.login('user1')
        src = self.membership.getHomeFolder('user1')
        src.invokeFactory('Document', id='testcopy')
        src.invokeFactory('Folder', id='dest')
        dest = src.dest
        dest.manage_pasteObjects(src.manage_copyObjects('testcopy'))

        # After a copy/paste, they should *both* have a copy
        self.assertTrue(hasattr(aq_base(src), 'testcopy'))
        self.assertTrue(hasattr(aq_base(dest), 'testcopy'))

    def testCopyOtherMemberContent(self):
        self.login('user1')
        src = self.membership.getHomeFolder('user1')
        src.invokeFactory('Document', id='testcopy')

        self.login('user2')
        dest = self.membership.getHomeFolder('user2')
        dest.manage_pasteObjects(src.manage_copyObjects('testcopy'))
        # After a copy/paste, they should *both* have a copy
        self.assertTrue(hasattr(aq_base(src), 'testcopy'))
        self.assertTrue(hasattr(aq_base(dest), 'testcopy'))

    def testCutMemberContent(self):
        self.login('user1')
        src = self.membership.getHomeFolder('user1')
        src.invokeFactory('Document', id='testcut')

        # We need to commit here so that _p_jar isn't None and move
        # will work
        transaction.savepoint(optimistic=True)

        src.invokeFactory('Folder', id='dest')
        dest = src.dest
        dest.manage_pasteObjects(src.manage_cutObjects('testcut'))

        # After a cut/paste, only destination has a copy
        self.assertFalse(hasattr(aq_base(src), 'testcut'))
        self.assertTrue(hasattr(aq_base(dest), 'testcut'))

    def testCutOtherMemberContent(self):
        self.login('user1')
        src = self.membership.getHomeFolder('user1')
        src.invokeFactory('Document', id='testcut')

        # We need to commit here so that _p_jar isn't None and move
        # will work
        transaction.savepoint(optimistic=True)

        self.login('user2')
        self.assertRaises(Unauthorized, src.restrictedTraverse,
                          'manage_cutObjects')

    def test_Bug2183_PastingIntoFolderFailsForNotAllowedContentTypes(self):
        # Test fix for http://dev.plone.org/plone/ticket/2183
        # The fix itself is in CMFCore.PortalFolder, not Plone

        # add the document to be copy and pasted later
        self.folder.invokeFactory('Document', 'doc')

        # add the folder where we try to paste the document later
        self.folder.invokeFactory('Folder', 'subfolder')
        subfolder = self.folder.subfolder

        # now disallow adding Document globaly
        types = self.portal.portal_types
        types.Document.manage_changeProperties(global_allow=0)

        # copy and pasting the object into the subfolder should raise
        # a ValueError.
        self.assertRaises(
            ValueError,
            subfolder.manage_pasteObjects,
            self.folder.manage_copyObjects(ids=['doc'])
        )

    def test_Bug2183_PastingIntoPortalFailsForNotAllowedContentTypes(self):
        # Test fix for http://dev.plone.org/plone/ticket/2183
        # The fix itself is in CMFCore.PortalFolder, not Plone

        # add the document to be copy and pasted later
        self.folder.invokeFactory('Document', 'doc')

        # now disallow adding Document globaly
        types = self.portal.portal_types
        types.Document.manage_changeProperties(global_allow=0)

        # need to be manager to paste into portal
        self.setRoles(['Manager'])

        # copy and pasting the object into the portal should raise
        # a ValueError.
        self.assertRaises(
            ValueError,
            self.portal.manage_pasteObjects,
            self.folder.manage_copyObjects(ids=['doc'])
        )


def failingEventHandler(obj, event):
    raise Exception("Failing for Testing")


class CutPasteFailureTests(PloneTestCase):
    """See https://dev.plone.org/ticket/9365"""

    def afterSetUp(self):
        self.folder.invokeFactory('Folder', id='source-folder')
        self.folder.invokeFactory('Folder', id='destination-folder')
        self.folder['source-folder'].invokeFactory('Document', id='doc')

    def testObject_pasteUncommitOnException(self):
        """Ensure that pasted objects aren't commited if an IObjectMovedEvent raises an exception.
        See https://dev.plone.org/ticket/9365
        """
        # register event handler
        provideHandler(failingEventHandler, [IContentish, IObjectMovedEvent])
        try:
            browser = self.getBrowser()
            browser.open(self.folder['source-folder']['doc'].absolute_url())
            browser.getLink('Cut').click()
            browser.open(self.folder['destination-folder'].absolute_url())
            try:
                browser.getLink('Paste').click()
            except HTTPError:
                # a HTTP 500 Server error is currently expected,
                # unless we find a better way to abort the
                # transaction.
                pass

            # test if document is not moved
            self.assertTrue('doc' in self.folder['source-folder'])
            self.assertFalse('doc' in self.folder['destination-folder'])

        finally:
            # unregister event handler
            getGlobalSiteManager().unregisterHandler(
                failingEventHandler, [IContentish, IObjectMovedEvent])

    def testFolder_pasteUncommitOnException(self):
        # register event handler
        provideHandler(failingEventHandler, [IContentish, IObjectMovedEvent])
        try:
            browser = self.getBrowser()
            browser.open(self.folder['source-folder']['doc'].absolute_url())
            browser.getLink('Cut').click()
            browser.open(self.folder['destination-folder'].absolute_url())
            try:
                browser.getLink('Paste').click()
            except HTTPError:
                # a HTTP 500 Server error is currently expected,
                # unless we find a better way to abort the
                # transaction.
                pass

            # test if document is not moved
            self.assertTrue('doc' in self.folder['source-folder'])
            self.assertFalse('doc' in self.folder['destination-folder'])

        finally:
            # unregister event handler
            getGlobalSiteManager().unregisterHandler(
                failingEventHandler, [IContentish, IObjectMovedEvent])
