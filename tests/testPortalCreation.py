#
# Tests portal creation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from OFS.SimpleItem import SimpleItem
from Acquisition import aq_base


class TestPortalCreation(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership

    def testPloneSkins(self):
        # Plone skins should have been set up
        self.failUnless(hasattr(self.folder, 'plone_powered.gif'))

    def testDefaultView(self):
        # index_html should render
        self.portal.index_html()

    def testWorkflowIsActionProvider(self):
        # XXX: This change has been backed out and the test inverted!
        # Remove portal_workflow by default.  We are falling back to
        # our use of the 'review_slot'.  There are no places using 
        # the worklist ui anymore directly from the listFilteredActionsFor
        at = self.portal.portal_actions
        self.failUnless('portal_workflow' in at.listActionProviders())

    def testReplyTabIsOff(self):
        # Ensure 'reply' tab is turned off
        # XXX NOTE: ActionProviderBAse should have a 'getActionById' 
        # that does this for x in: if x == id
        dt_actions = self.portal.portal_discussion.listActions()
        reply_visible=1
        for action in dt_actions:
            if action.id=='reply':
                reply_visible=action.visible
        self.assertEqual(reply_visible, 0)


class TestPortalBugs(PloneTestCase.PloneTestCase):
    
    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.members = self.membership.getMembersFolder()
        # Fake the Members folder contents
        self.members._setObject('index_html', ZopePageTemplate('index_html'))

    def testMembersIndexHtml(self):
        # index_html for Members folder should be a Page Template
        members = self.members
        self.assertEqual(aq_base(members).meta_type, 'Large Plone Folder')
        self.failUnless(hasattr(aq_base(members), 'index_html'))
        # getitem works
        self.assertEqual(aq_base(members)['index_html'].meta_type, 'Page Template')
        self.assertEqual(members['index_html'].meta_type, 'Page Template')
        # _getOb works
        self.assertEqual(aq_base(members)._getOb('index_html').meta_type, 'Page Template')
        self.assertEqual(members._getOb('index_html').meta_type, 'Page Template')
        # getattr works when called explicitly
        self.assertEqual(aq_base(members).__getattr__('index_html').meta_type, 'Page Template')
        self.assertEqual(members.__getattr__('index_html').meta_type, 'Page Template')

    def testLargePloneFolderHickup(self):
        # Attribute access for 'index_html' acquired the Document from the
        # portal instead of returning the local Page Template. This was due to
        # special treatment of 'index_html' in the PloneFolder base class and
        # got fixed by hazmat.
        members = self.members
        self.assertEqual(aq_base(members).meta_type, 'Large Plone Folder')
        #self.assertEqual(members.index_html.meta_type, 'Document')
        self.assertEqual(members.index_html.meta_type, 'Page Template')

    def testManageBeforeDeleteIsCalledRecursively(self):
        # When the portal is deleted, all subobject should have 
        # their manage_beforeDelete hook called. Fixed by geoffd.
        self.folder._setObject('dummy', DummyObject())
        self.dummy = self.folder.dummy
        self.app._delObject(PloneTestCase.portal_name)
        self.assertEqual(self.dummy.mbd_called, 1)


# Test helpers

class DummyObject(SimpleItem):
    mbd_called = 0
    def __init__(self, id='dummy'): 
        self.id = id
    def manage_beforeDelete(self, item, container): 
        self.mbd_called = 1


if __name__ == '__main__':
    framework()
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestPortalCreation))
        suite.addTest(makeSuite(TestPortalBugs))
        return suite

