#
# Tests portal creation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from OFS.SimpleItem import SimpleItem
from Acquisition import aq_base


class TestPortalCreation(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.workflow = self.portal.portal_workflow
        self.types = self.portal.portal_types
        self.cp = self.portal.portal_controlpanel
        self.actions = self.portal.portal_actions
        self.icons = self.portal.portal_actionicons
        self.properties = self.portal.portal_properties
        self.memberdata = self.portal.portal_memberdata
        self.catalog = self.portal.portal_catalog
        self.groups = self.portal.portal_groups
        self.factory = self.portal.portal_factory

    def testPloneSkins(self):
        # Plone skins should have been set up
        self.failUnless(hasattr(self.folder, 'plone_powered.gif'))

    def testDefaultSkin(self):
        # index_html should render
        self.portal.index_html()

    def testNoIndexHtmlDocument(self):
        # The portal should not contain an index_html Document
        self.failIf('index_html' in self.portal.objectIds())

    def testCanViewManagementScreen(self):
        # Make sure the ZMI management screen works
        self.portal.manage_main()

    def testControlPanelGroups(self):
        # Test for https://plone.org/collector/2749
        # Wake up object, in the case it was deactivated.
        dir(self.cp); dir(self.cp)
        self.failUnless(self.cp.__dict__.has_key('groups'))

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

    def testLargePloneFolderWorkflow(self):
        # Large Plone Folder should use folder_workflow
        # http://plone.org/collector/2744
        lpf_chain = self.workflow.getChainFor('Large Plone Folder')
        self.failUnless('folder_workflow' in lpf_chain)
        self.failIf('plone_workflow' in lpf_chain)

    def testMembersFolderMetaType(self):
        # Members folder should have meta_type 'Large Plone Folder'
        members = self.membership.getMembersFolder()
        #self.assertEqual(members.meta_type, 'Large Plone Folder')
        self.assertEqual(members.meta_type, 'ATBTreeFolder')

    def testMembersFolderPortalType(self):
        # Members folder should have portal_type 'Large Plone Folder'
        members = self.membership.getMembersFolder()
        self.assertEqual(members._getPortalTypeName(), 'Large Plone Folder')

    def testMembersFolderMeta(self):
        # Members folder should have title 'Members'
        members = self.membership.getMembersFolder()
        self.assertEqual(members.getId(), 'Members')
        self.assertEqual(members.Title(), 'Members')

    def testMembersFolderIsIndexed(self):
        # Members folder should be cataloged
        res = self.catalog(id='Members')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'Members')
        self.assertEqual(res[0].Title, 'Members')

    def testSecureMailHost(self):
        # MailHost should be of the SMH variety
        mailhost = self.portal.plone_utils.getMailHost()
        self.assertEqual(mailhost.meta_type, 'Secure Mail Host')

    def testUseFolderContentsProperty(self):
        # The use_folder_contents site property should be emtpy
        props = self.portal.portal_properties.site_properties
        self.assertEqual(props.getProperty('use_folder_contents'), ())

    def testFolderEditActionHasEditTitle(self):
        # Edit tab of folders should be named 'edit', not 'properties'
        folder = self.types.getTypeInfo('Folder')
        for action in folder._cloneActions():
            if action.id == 'edit':
                self.assertEqual(action.title, 'Edit')
                break
        else:
            self.fail("Folder has no 'edit' action")

    def testFolderEditActionBeforeSharing(self):
        # Edit tab of folders should appear before the sharing tab
        folder = self.types.getTypeInfo('Folder')
        i = j = count = 0
        for action in folder._cloneActions():
            if action.id == 'local_roles':
                i = count
            elif action.id == 'edit':
                j = count
            count += 1
        self.failUnless(j < i)

    def testFolderHasFolderListingAction(self):
        # Folders should have a 'folderlisting' action
        topic = self.types.getTypeInfo('Folder')
        for action in topic._cloneActions():
            if action.id == 'folderlisting':
                break
        else:
            self.fail("Folder has no 'folderlisting' action")

    def testTopicHasFolderListingAction(self):
        # Topics should have a 'folderlisting' action
        topic = self.types.getTypeInfo('Topic')
        for action in topic._cloneActions():
            if action.id == 'folderlisting':
                break
        else:
            self.fail("Topic has no 'folderlisting' action")

    def testImagePatch(self):
        # Is it ok to remove the imagePatch? Probably not as we
        # don't want the border attribute ...
        self.folder.invokeFactory('Image', id='foo', file=dummy.Image())
        endswith = ' alt="" title="" height="16" width="16" />'
        self.assertEqual(self.folder.foo.tag()[-len(endswith):], endswith)

    def testNoPortalFormTool(self):
        # portal_form should have been removed
        self.failIf('portal_form' in self.portal.objectIds())

    def testNoPortalNavigationTool(self):
        # portal_navigation should have been removed
        self.failIf('portal_navigation' in self.portal.objectIds())

    def testNoFormProperties(self):
        # form_properties should have been removed
        self.failIf('form_properties' in self.properties.objectIds())

    def testNoNavigationProperties(self):
        # navigation_properties should have been removed
        self.failIf('navigation_properties' in self.properties.objectIds())

    def testFullScreenAction(self):
        # There should be a full_screen action
        for action in self.actions.listActions():
            if action.getId() == 'full_screen':
                break
        else:
            self.fail("Actions tool has no 'full_screen' action")

    def testFullScreenActionIcon(self):
        # There should be a full_screen action icon
        for icon in self.icons.listActionIcons():
            if icon.getActionId() == 'full_screen':
                break
        else:
            self.fail("Action icons tool has no 'full_screen' icon")

    def testVisibleIdsSiteProperty(self):
        # visible_ids should be a site property, not a memberdata property
        self.failUnless(self.properties.site_properties.hasProperty('visible_ids'))
        self.failIf(self.memberdata.hasProperty('visible_ids'))

    def testFormToolTipsProperty(self):
        # formtooltips should have been removed
        self.failIf(self.memberdata.hasProperty('formtooltips'))

    def testNavTreeProperties(self):
        # navtree_properties should contain the new properties
        self.failUnless(self.properties.navtree_properties.hasProperty('typesToList'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sortAttribute'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sortOrder'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sitemapDepth'))
        self.failUnless(self.properties.navtree_properties.hasProperty('showAllParents'))

    def testSitemapAction(self):
        # There should be a sitemap action
        for action in self.actions.listActions():
            if action.getId() == 'sitemap':
                break
        else:
            self.fail("Actions tool has no 'sitemap' action")

    def testResourceRegistries(self):
        # We should have portal_css and portal_javascripts tools
        self.failUnless(hasattr(self.portal, 'portal_css'))
        self.failUnless(hasattr(self.portal, 'portal_javascripts'))

    def testUnfriendlyTypesProperty(self):
        # We should have an types_not_searched property
        self.failUnless(self.properties.site_properties.hasProperty('types_not_searched'))
        self.failUnless('Plone Site' in self.properties.site_properties.getProperty('types_not_searched'))

    def testNonDefaultPageTypes(self):
        # We should have a non_default_page_types property
        self.failUnless(self.properties.site_properties.hasProperty('non_default_page_types'))
        self.failUnless('Folder' in self.properties.site_properties.getProperty('non_default_page_types'))
        self.failUnless('Large Plone Folder' in self.properties.site_properties.getProperty('non_default_page_types'))

    def testNoMembersAction(self):
        # There should not be a Members action
        for action in self.actions.listActions():
            if action.getId() == 'Members':
                self.fail("Actions tool still has 'Members' action")

    def testNoNewsAction(self):
        # There should not be a news action
        for action in self.actions.listActions():
            if action.getId() == 'news':
                self.fail("Actions tool still has 'News' action")

    def testNewsFolder(self):
        # The portal should contain news folder
        self.failUnless('news' in self.portal.objectIds())
        news = getattr(self.portal.aq_base, 'news')
        self.assertEqual(news._getPortalTypeName(), 'Large Plone Folder')
        self.assertEqual(news.Title(), 'News')
        self.assertEqual(news.Description(), 'Site News')
        self.assertEqual(list(news.getProperty('default_page')), ['news_topic','news_listing','index_html'])
        self.assertEqual(list(news.getImmediatelyAddableTypes()),['News Item'])
        self.assertEqual(list(news.getLocallyAllowedTypes()),['News Item'])
        self.assertEqual(news.getConstrainTypesMode(), 1)

    def testNewsFolderIsIndexed(self):
        # News folder should be cataloged
        res = self.catalog(id='news')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'news')
        self.assertEqual(res[0].Title, 'News')
        self.assertEqual(res[0].Description, 'Site News')

    def testNewsTopic(self):
        # News topic is in place as default view and has a criterion to show
        # only News Items.
        news = self.portal.news
        self.failUnless('news_topic' in news.objectIds())
        topic = getattr(news.aq_base, 'news_topic')
        self.assertEqual(topic._getPortalTypeName(), 'Topic')
        self.assertEqual(topic.buildQuery()['Type'], ('News Item',))

    def testEventsFolder(self):
        # The portal should contain events folder
        self.failUnless('events' in self.portal.objectIds())
        events = getattr(self.portal.aq_base, 'events')
        self.assertEqual(events._getPortalTypeName(), 'Large Plone Folder')
        self.assertEqual(events.Title(), 'Events')
        self.assertEqual(events.Description(), 'Site Events')
        self.assertEqual(list(events.getProperty('default_page')), ['events_topic','events_listing','index_html'])
        self.assertEqual(list(events.getImmediatelyAddableTypes()),['Event'])
        self.assertEqual(list(events.getLocallyAllowedTypes()),['Event'])
        self.assertEqual(events.getConstrainTypesMode(), 1)

    def testEventsFolderIsIndexed(self):
        # Events folder should be cataloged
        res = self.catalog(id='events')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'events')
        self.assertEqual(res[0].Title, 'Events')
        self.assertEqual(res[0].Description, 'Site Events')

    def testEventsTopic(self):
        # Events topic is in place as default view and has a criterion to show
        # only Events Items.
        events = self.portal.events
        self.failUnless('events_topic' in events.objectIds())
        topic = getattr(events.aq_base, 'events_topic')
        self.assertEqual(topic._getPortalTypeName(), 'Topic')
        self.assertEqual(topic.buildQuery()['Type'], ('Event',))

    def testObjectButtonActions(self):
        installed = [(a.getId(), a.getCategory()) for a in self.actions.listActions()]
        self.failUnless(('cut', 'object_buttons') in installed)
        self.failUnless(('copy', 'object_buttons') in installed)
        self.failUnless(('paste', 'object_buttons') in installed)
        self.failUnless(('delete', 'object_buttons') in installed)

    def testBatchActions(self):
        installed = [(a.getId(), a.getCategory()) for a in self.actions.listActions()]
        self.failUnless(('batch', 'batch') in installed)

    def testContentsTabDisabled(self):
        for a in self.actions.listActions():
            if a.getId() == 'contents':
                self.failIf(a.visible)
                
    def testDefaultGroupsAdded(self):
        self.failUnless('Administrators' in self.groups.listGroupIds())
        self.failUnless('Reviewers' in self.groups.listGroupIds())

    def testDefaultTypesInPortalFactory(self):
        types = self.factory.getFactoryTypes().keys()
        for metaType in ('Document', 'Event', 'File', 'Folder', 'Image', 
                         'Folder', 'Large Plone Folder', 'Link', 'News Item',
                         'Topic'):
            self.failUnless(metaType in types)

    def testAllDependenciesMet(self):
        from Products.CMFPlone.setup import dependencies
        msgs = [x for x in dependencies.messages if not x['optional']]
        self.failUnlessEqual(msgs, [])

    def testDisableFolderSectionsSiteProperty(self):
        # The disable_folder_sections site property should be emtpy
        props = self.portal.portal_properties.site_properties
        self.failUnless(props.getProperty('disable_folder_sections', None) is not None)
        self.failIf(props.getProperty('disable_folder_sections'))
        
    def testSelectableViewsPropertyAtPortalRoot(self):
        views = self.portal.getProperty('selectable_views', [])
        self.failUnless(len(views) == 2)
        self.failUnless('folder_listing' in views)
        self.failUnless('news_listing' in views)
        


class TestPortalBugs(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.members = self.membership.getMembersFolder()
        # Fake the Members folder contents
        self.members._setObject('index_html', ZopePageTemplate('index_html'))

    def testMembersIndexHtml(self):
        # index_html for Members folder should be a Page Template
        members = self.members
        #self.assertEqual(aq_base(members).meta_type, 'Large Plone Folder')
        self.assertEqual(aq_base(members).meta_type, 'ATBTreeFolder')
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
        self.assertEqual(aq_base(members).meta_type, 'ATBTreeFolder')
        #self.assertEqual(members.index_html.meta_type, 'Document')
        self.assertEqual(members.index_html.meta_type, 'Page Template')

    def testManageBeforeDeleteIsCalledRecursively(self):
        # When the portal is deleted, all subobject should have
        # their manage_beforeDelete hook called. Fixed by geoffd.
        self.folder._setObject('foo', dummy.DeletedItem())
        self.foo = self.folder.foo
        self.app._delObject(PloneTestCase.portal_name)
        self.failUnless(self.foo.before_delete_called())


class TestManagementPageCharset(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.properties = self.portal.portal_properties

    def testManagementPageCharsetEqualsDefaultCharset(self):
        # Checks that 'management_page_charset' attribute of the portal
        # reflects 'portal_properties/site_properties/default_charset'.
        default_charset = self.properties.site_properties.getProperty('default_charset', None)
        self.failUnless(default_charset)
        manage_charset = getattr(self.portal, 'management_page_charset', None)
        self.failUnless(manage_charset)
        self.assertEqual(manage_charset, default_charset)
        self.assertEqual(manage_charset, 'utf-8')

    def testManagementPageCharsetIsComputedAttribute(self):
        # Checks that 'management_page_charset' attribute of the portal
        # is a ComputedAttribute and always follows the default_charset property.
        self.properties.site_properties.manage_changeProperties(default_charset='latin1')
        default_charset = self.properties.site_properties.getProperty('default_charset', None)
        manage_charset = getattr(self.portal, 'management_page_charset', None)
        self.assertEqual(manage_charset, default_charset)
        self.assertEqual(manage_charset, 'latin1')

    def testManagementPageCharsetFallbackNoProperty(self):
        self.properties.site_properties._delProperty('default_charset')
        manage_charset = getattr(self.portal, 'management_page_charset', None)
        self.assertEqual(manage_charset, 'utf-8')

    def testManagementPageCharsetFallbackNoPropertySheet(self):
        self.properties._delObject('site_properties')
        manage_charset = getattr(self.portal, 'management_page_charset', None)
        self.assertEqual(manage_charset, 'utf-8')

    def testManagementPageCharsetFallbackNotAPropertySheet(self):
        self.properties._delObject('site_properties')
        self.properties.site_properties = 'foo'
        manage_charset = getattr(self.portal, 'management_page_charset', None)
        self.assertEqual(manage_charset, 'utf-8')

    def testManagementPageCharsetFallbackNoPropertyTool(self):
        self.portal._delObject('portal_properties')
        manage_charset = getattr(self.portal, 'management_page_charset', None)
        self.assertEqual(manage_charset, 'utf-8')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortalCreation))
    suite.addTest(makeSuite(TestPortalBugs))
    suite.addTest(makeSuite(TestManagementPageCharset))
    return suite

if __name__ == '__main__':
    framework()
