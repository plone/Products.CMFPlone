#
# Test methods used to make ...
#

from zope.interface import directlyProvides, noLongerProvides

from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.interfaces.NonStructuralFolder import \
     INonStructuralFolder as z2INonStructuralFolder
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from Products.CMFPlone.browser.ploneview import Plone

from Products.CMFPlone.ActionsTool import ActionsTool
from Products.CMFPlone.InterfaceTool import InterfaceTool
from Products.CMFPlone.MembershipTool import MembershipTool
from Products.CMFPlone.SyndicationTool import SyndicationTool
from Products.CMFPlone.URLTool import URLTool
from Products.CMFCore.WorkflowTool import WorkflowTool

from zope.publisher.browser import setDefaultSkin

class TestPloneView(PloneTestCase.PloneTestCase):
    """Tests the global plone view.  All the old global_defines should be
       in the _data mapping of the view, which is globablized into
       calling templates."""

    def afterSetUp(self):
        # We need to fiddle the request for zope 2.9+
        setDefaultSkin(self.app.REQUEST)
        self.folder.invokeFactory('Document', 'test',
                                  title='Test default page')
        self.view = Plone(self.portal, self.app.REQUEST)
        self.view._initializeData()

    def testUTool(self):
        assert isinstance(self.view._data['utool'], URLTool)

    def testPortal(self):
        assert self.view._data['portal'] == self.portal

    def testPortalURL(self):
        assert isinstance(self.view._data['portal_url'], type(''))

    def testMTool(self):
        assert isinstance(self.view._data['mtool'], MembershipTool)

    def testATool(self):
        assert isinstance(self.view._data['atool'], ActionsTool)

    def testPUtils(self):
        pass

    def testWTool(self):
        assert isinstance(self.view._data['wtool'], WorkflowTool)

    def testIFaceTool(self):
        assert isinstance(self.view._data['ifacetool'], InterfaceTool)

    def testSynTool(self):
        assert isinstance(self.view._data['syntool'], SyndicationTool)

    def testPortalTitle(self):
        pass

    def testToLocalizedTime(self):
        localdate = self.view.toLocalizedTime
        value = localdate('Mar 9, 1997 1:45pm', long_format=True)
        self.assertEquals(value, 'Mar 09, 1997 01:45 PM')

    def testIsStructuralFolderWithNonFolder(self):
        i = dummy.Item()
        self.failIf(Plone(i, self.app.REQUEST).isStructuralFolder())

    def testIsStructuralFolderWithFolder(self):
        f = dummy.Folder('struct_folder')
        self.failUnless(Plone(f, self.app.REQUEST).isStructuralFolder())

    def testIsStructuralFolderWithNonStructuralFolder(self):
        f = dummy.NonStructuralFolder('ns_folder')
        self.failIf(Plone(f, self.app.REQUEST).isStructuralFolder())

    def testIsStructuralFolderWithZ2NonStructuralFolder(self):
        f = dummy.Folder('z2_nsFolder')
        f.__implements__ = f.__implements__ + (z2INonStructuralFolder,)
        view = Plone(f, self.app.REQUEST)
        value = view.isStructuralFolder()
        self.failIf(Plone(f, self.app.REQUEST).isStructuralFolder())

    def testIsDefaultPageInFolder(self):
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failIf(view.isDefaultPageInFolder())
        self.failUnless(self.folder.canSelectDefaultPage())
        self.folder.saveDefaultPage('test')
        # re-create the view, because the old value is cached
        del self.app.REQUEST.__annotations__
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failUnless(view.isDefaultPageInFolder())

    def testNavigationRootPath(self):
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.navigationRootPath(), self.portal.portal_url.getPortalPath())

    def testNavigationRootUrl(self):
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.navigationRootUrl(), self.portal.absolute_url())

    def testGetParentObject(self):
        view = Plone(self.folder.test, self.app.REQUEST)
        self.assertEqual(view.getParentObject(), self.folder)
        # Make sure this looks only at containment
        del self.app.REQUEST.__annotations__
        view = Plone(self.folder.test.__of__(self.portal), self.app.REQUEST)
        self.assertEqual(view.getParentObject(), self.folder)

    def testIsFolderOrFolderDefaultPage(self):
        # an actual folder whould return true
        view = Plone(self.folder, self.app.REQUEST)
        self.failUnless(view.isFolderOrFolderDefaultPage())
        # But not a document
        del self.app.REQUEST.__annotations__
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failIf(view.isFolderOrFolderDefaultPage())
        # Unless we make it the default view
        self.folder.saveDefaultPage('test')
        del self.app.REQUEST.__annotations__
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failUnless(view.isFolderOrFolderDefaultPage())
        # And if we have a non-structural folder it should not be true
        f = dummy.NonStructuralFolder('ns_folder')
        self.folder._setObject('ns_folder', f)
        del self.app.REQUEST.__annotations__
        view = Plone(self.folder.ns_folder, self.app.REQUEST)
        self.failIf(view.isFolderOrFolderDefaultPage())

    def testIsPortalOrPortalDefaultPage(self):
        # an actual folder whould return true
        view = Plone(self.portal, self.app.REQUEST)
        self.failUnless(view.isPortalOrPortalDefaultPage())
        # But not a document
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'portal_test',
                                  title='Test default page')
        del self.app.REQUEST.__annotations__
        view = Plone(self.portal.portal_test, self.app.REQUEST)
        self.failIf(view.isPortalOrPortalDefaultPage())
        # Unless we make it the default view
        self.portal.saveDefaultPage('portal_test')
        del self.app.REQUEST.__annotations__
        view = Plone(self.portal.portal_test, self.app.REQUEST)
        self.failUnless(view.isPortalOrPortalDefaultPage())

    def testGetCurrentFolder(self):
        # If context is a folder, then the folder is returned
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)
        
        # If context is not a folder, then the parent is returned
        # A bit crude ... we need to make sure our memos don't stick in the tests
        del self.app.REQUEST.__annotations__
        view = Plone(self.folder.test, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)
        
        # The real container is returned regardless of context
        del self.app.REQUEST.__annotations__
        view = Plone(self.folder.test.__of__(self.portal), self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)
        
        # A non-structural folder does not count as a folder`
        f = dummy.NonStructuralFolder('ns_folder')
        self.folder._setObject('ns_folder', f)
        del self.app.REQUEST.__annotations__
        view = Plone(self.folder.ns_folder, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)
        
        # And even a structural folder that is used as a default page
        # returns its parent
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Topic', 'topic')
        
        del self.app.REQUEST.__annotations__
        view = Plone(self.folder.topic, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder.topic)
        self.folder.saveDefaultPage('topic')
        
        del self.app.REQUEST.__annotations__
        view = Plone(self.folder.topic, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)

    def testHavePortlets(self):
        view = Plone(self.portal, self.app.REQUEST)
        self.assertEqual(False, view.have_portlets('plone.leftcolumn'))
        self.assertEqual(True, view.have_portlets('plone.rightcolumn'))

    def testDisablePortlets(self):
        view = Plone(self.portal, self.app.REQUEST)
        view._initializeData()
        data = view._data
        self.assertEqual(True, data['sr'])
        self.assertEqual('visualColumnHideOne', data['hidecolumns'])
        view._initializeData(options={'no_portlets': True})
        self.assertEqual(False, data['sr'])
        self.assertEqual('visualColumnHideOneTwo', data['hidecolumns'])

    def testCropText(self):
        view = Plone(self.portal, self.app.REQUEST)
        self.assertEqual(view.cropText('Hello world', 7), 'Hello ...')
        self.assertEqual(view.cropText('Hello world', 99), 'Hello world')
        self.assertEqual(view.cropText('Hello world', 10), 'Hello worl...')
        self.assertEqual(view.cropText(u'Hello world', 10), u'Hello worl...')
        self.assertEqual(view.cropText(u'Koko\u0159\xedn', 5), u'Koko\u0159...')
        # Test utf encoded string Kokorin with 'r' and 'i' accented 
        # Must return 6 characters, because 5th character is two byte
        text = u'Koko\u0159\xedn'.encode('utf8')
        self.assertEqual(view.cropText(text, 5), 'Koko\xc5\x99...')
    
    def testUniqueIndexIterator(self):
        iterator = self.view._data['uniqueItemIndex']
        self.assertEquals(0, iterator.next())
        self.assertEquals(1, iterator.next())
        self.assertEquals(2, iterator.next())
        
    def testPrepareObjectTabsOnPortalRoot(self):
        del self.app.REQUEST.__annotations__
        self.loginAsPortalOwner()
        self.app.REQUEST['ACTUAL_URL'] = self.portal.absolute_url()
        view = self.portal.restrictedTraverse('@@plone')
        tabs = view.prepareObjectTabs()
        self.assertEquals(tabs[0]['id'], 'folderContents')
        self.assertEquals(['view'], [t['id'] for t in tabs if t['selected']])
        
    def testPrepareObjectTabsNonFolder(self):
        del self.app.REQUEST.__annotations__
        self.loginAsPortalOwner()
        self.app.REQUEST['ACTUAL_URL'] = self.folder.test.absolute_url()
        view = self.folder.test.restrictedTraverse('@@plone')
        tabs = view.prepareObjectTabs()
        self.assertEquals(0, len([t for t in tabs if t['id'] == 'folderContents']))
        self.assertEquals(['view'], [t['id'] for t in tabs if t['selected']])
        
    def testPrepareObjectTabsNonStructuralFolder(self):
        del self.app.REQUEST.__annotations__
        self.loginAsPortalOwner()
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url()
        directlyProvides(self.folder, INonStructuralFolder)
        view = self.folder.restrictedTraverse('@@plone')
        tabs = view.prepareObjectTabs()
        noLongerProvides(self.folder, INonStructuralFolder)
        self.assertEquals(0, len([t for t in tabs if t['id'] == 'folderContents']))
        self.assertEquals(['view'], [t['id'] for t in tabs if t['selected']])
        
    def testPrepareObjectTabsDefaultView(self):
        del self.app.REQUEST.__annotations__
        self.loginAsPortalOwner()
        self.app.REQUEST['ACTUAL_URL'] = self.folder.test.absolute_url() + '/edit'
        view = self.folder.test.restrictedTraverse('@@plone')
        tabs = view.prepareObjectTabs()
        self.assertEquals(0, len([t for t in tabs if t['id'] == 'folderContents']))
        self.assertEquals(['edit'], [t['id'] for t in tabs if t['selected']])

    def testActionOverrideFromTemplate(self):
        # We should be able to pass actions in from the template
        # and have them override the calculated actions
        view = Plone(self.portal, self.app.REQUEST)
        view._initializeData()
        data = view._data
        self.failUnless(data['actions'])
        self.failUnless(data['keyed_actions'])
        self.failUnless(data['user_actions'])
        no_actions = {'folder':[], 'user':[], 'global':[], 'workflow':[]}
        view._initializeData(options={'actions':no_actions})
        self.assertEqual(data['actions'], no_actions)
        self.assertEqual(data['keyed_actions'], no_actions)
        self.failIf(data['user_actions'])


class TestVisibleIdsEnabled(PloneTestCase.PloneContentLessTestCase):
    '''Tests the visibleIdsEnabled method'''

    def afterSetUp(self):
        self.view = Plone(self.portal, self.app.REQUEST)
        self.member = self.portal.portal_membership.getAuthenticatedMember()
        self.props = self.portal.portal_properties.site_properties

    def testFailsWithSitePropertyDisabled(self):
        # Set baseline
        self.member.setProperties(visible_ids=False)
        self.props.manage_changeProperties(visible_ids=False)
        # Should fail when site property is set false
        self.failIf(self.view.visibleIdsEnabled())
        self.member.setProperties(visible_ids=True)
        self.failIf(self.view.visibleIdsEnabled())

    def testFailsWithMemberPropertyDisabled(self):
        # Should fail when member property is false
        self.member.setProperties(visible_ids=False)
        self.props.manage_changeProperties(visible_ids=True)
        self.failIf(self.view.visibleIdsEnabled())

    def testSucceedsWithMemberAndSitePropertyEnabled(self):
        # Should succeed only when site property and member property are true
        self.props.manage_changeProperties(visible_ids=True)
        self.member.setProperties(visible_ids=True)
        self.failUnless(self.view.visibleIdsEnabled())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneView))
    suite.addTest(makeSuite(TestVisibleIdsEnabled))
    return suite
