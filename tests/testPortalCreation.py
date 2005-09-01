#
# Tests portal creation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFCore import CMFCorePermissions
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from OFS.SimpleItem import SimpleItem
from Acquisition import aq_base
from DateTime import DateTime


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
        self.cc = self.portal.cookie_authentication
        self.skins = self.portal.portal_skins

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

    def testVisibleIdsProperties(self):
        # visible_ids should be a site property and a memberdata property
        self.failUnless(self.properties.site_properties.hasProperty('visible_ids'))
        self.failUnless(self.memberdata.hasProperty('visible_ids'))

    def testFormToolTipsProperty(self):
        # formtooltips should have been removed
        self.failIf(self.memberdata.hasProperty('formtooltips'))

    def testNavTreeProperties(self):
        # navtree_properties should contain the new properties
        self.failUnless(self.properties.navtree_properties.hasProperty('metaTypesNotToList'))
        self.failUnless(self.properties.navtree_properties.hasProperty('parentMetaTypesNotToQuery'))
        self.failUnless('Large Plone Folder' in
                            self.properties.navtree_properties.getProperty('parentMetaTypesNotToQuery'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sortAttribute'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sortOrder'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sitemapDepth'))
        self.failUnless(self.properties.navtree_properties.hasProperty('showAllParents'))
        self.failUnless(self.properties.navtree_properties.hasProperty('wf_states_to_show'))
        self.failUnless(self.properties.navtree_properties.hasProperty('enable_wf_state_filtering'))

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
        self.failUnless('CMF Document' in self.properties.site_properties.getProperty('types_not_searched'))

    def testNonDefaultPageTypes(self):
        # We should have a default_page_types property
        self.failUnless(self.properties.site_properties.hasProperty('default_page_types'))
        self.failUnless('Folder' not in self.properties.site_properties.getProperty('default_page_types'))
        self.failUnless('Large Plone Folder' not in self.properties.site_properties.getProperty('default_page_types'))
        self.failUnless('Topic' in self.properties.site_properties.getProperty('default_page_types'))
        self.failUnless('Document' in self.properties.site_properties.getProperty('default_page_types'))

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

    def testNewsFolderIsIndexed(self):
        # News folder should be cataloged
        res = self.catalog(id='news')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'news')
        self.assertEqual(res[0].Title, 'News')
        self.assertEqual(res[0].Description, 'Site News')

    def testNewsTopic(self):
        # News topic is in place as default view and has a criterion to show
        # only News Items, and uses the folder_summary_view.
        self.failUnless('news' in self.portal.objectIds())
        topic = getattr(self.portal.aq_base, 'news')
        self.assertEqual(topic._getPortalTypeName(), 'Topic')
        self.assertEqual(topic.buildQuery()['Type'], ('News Item',))
        self.assertEqual(topic.buildQuery()['review_state'], 'published')
        self.assertEqual(topic.getLayout(), 'folder_summary_view')

    def testEventsTopic(self):
        # Events topic is in place as default view and has criterion to show
        # only future Events Items.
        self.failUnless('events' in self.portal.objectIds())
        topic = self.portal.events
        self.assertEqual(topic._getPortalTypeName(), 'Topic')
        query = topic.buildQuery()
        self.assertEqual(query['Type'], ('Event',))
        self.assertEqual(query['review_state'], 'published')
        self.assertEqual(query['start']['query'].Date(), DateTime().Date())
        self.assertEqual(query['start']['range'], 'min')

    def testEventsSubTopic(self):
        # past Events sub-topic is in place and has criteria to show
        # only past Events Items.
        events_topic = self.portal.events
        self.failUnless('previous' in events_topic.objectIds())
        topic = getattr(events_topic.aq_base, 'previous')
        self.assertEqual(topic._getPortalTypeName(), 'Topic')
        query = topic.buildQuery()
        self.assertEqual(query['Type'], ('Event',))
        self.assertEqual(query['review_state'], 'published')
        self.assertEqual(query['start']['query'].Date(), DateTime().Date())
        self.assertEqual(query['start']['range'], 'max')

    def testObjectButtonActions(self):
        installed = [(a.getId(), a.getCategory()) for a in self.actions.listActions()]
        self.failUnless(('cut', 'object_buttons') in installed)
        self.failUnless(('copy', 'object_buttons') in installed)
        self.failUnless(('paste', 'object_buttons') in installed)
        self.failUnless(('delete', 'object_buttons') in installed)

    def testContentsTabVisible(self):
        for a in self.actions.listActions():
            if a.getId() == 'folderContents':
                self.failUnless(a.visible)

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

    def testSelectableViewsOnFolder(self):
        views = self.portal.portal_types.Folder.getAvailableViewMethods(None)
        self.failUnless('folder_listing' in views)
        self.failUnless('atct_album_view' in views)

    def testSelectableViewsOnTopic(self):
        views = self.portal.portal_types.Topic.getAvailableViewMethods(None)
        self.failUnless('folder_listing' in views)
        self.failUnless('atct_album_view' in views)
        self.failUnless('atct_topic_view' in views)

    def testLocationMemberdataProperty(self):
        # portal_memberdata should have a location property
        self.failUnless(self.memberdata.hasProperty('location'))

    def testLanguageMemberdataProperty(self):
        # portal_memberdata should have a language property
        self.failUnless(self.memberdata.hasProperty('language'))

    def testDescriptionMemberdataProperty(self):
        # portal_memberdata should have a description property
        self.failUnless(self.memberdata.hasProperty('description'))

    def testHome_PageMemberdataProperty(self):
        # portal_memberdata should have a home_page property
        self.failUnless(self.memberdata.hasProperty('home_page'))

    def testExtEditorMemberdataProperty(self):
        # portal_memberdata should have a location property
        self.assertEqual(self.memberdata.getProperty('ext_editor'), 0)

    def testChangeStateIsLastFolderButton(self):
        # Change state button should be the last
        actions = [x for x in self.actions.listActions() if
                    x.category == 'folder_buttons']
        self.assertEqual(actions[-1].id, 'change_state', [x.id for x in actions])

    def testTypesUseViewActionInListingsProperty(self):
        # site_properties should have the typesUseViewActionInListings property
        self.failUnless(self.properties.site_properties.hasProperty('typesUseViewActionInListings'))

    def testSiteSetupAction(self):
        # There should be a Site Setup action
        for action in self.actions.listActions():
            if action.getId() == 'plone_setup':
                self.assertEqual(action.title, 'Site Setup')
                break
        else:
            self.fail("Actions tool has no 'sitemap' action")

    def testFolderlistingAction(self):
        # Make sure the folderlisting action of a Folder is /view, to ensure
        # that the layout template will be resolved (see PloneTool.browserDefault)
        self.assertEqual(self.types['Folder'].getActionById('folderlisting'), 'view')
        self.assertEqual(self.types['Plone Site'].getActionById('folderlisting'), 'view')

    def testEnableLivesearchProperty(self):
        # site_properties should have enable_livesearch property
        self.failUnless(self.properties.site_properties.hasProperty('enable_livesearch'))

    def testSearchSettingsActionIcon(self):
        # There should be a SearchSettings action icon
        for icon in self.icons.listActionIcons():
            if icon.getActionId() == 'SearchSettings':
                break
        else:
            self.fail("Action icons tool has no 'SearchSettings' icon")

    def testCookieCrumblerProperties(self):
        # Cookie Crumbler should have unauth_page set to insufficient privileges
        # and the auto login page restored to login_form
        self.assertEqual(self.cc.getProperty('unauth_page'), 'insufficient_privileges')
        self.assertEqual(self.cc.getProperty('auto_login_page'), 'login_form')

    def testPortalFTIIsDynamicFTI(self):
        # Plone Site FTI should be a DynamicView FTI
        fti = self.portal.getTypeInfo()
        self.assertEqual(fti.meta_type, 'Factory-based Type Information with dynamic views')

    def testPloneSiteFTIHasMethodAliases(self):
        # Should add method aliases to the Plone Site FTI
        expected_aliases = {
                '(Default)'  : '(dynamic view)',
                'view'       : '(selected layout)',
                'index.html' : '(dynamic view)',
                'edit'       : 'folder_edit_form',
                'sharing'    : 'folder_localrole_form',
              }
        fti = self.portal.getTypeInfo()
        aliases = fti.getMethodAliases()
        self.assertEqual(aliases, expected_aliases)

    def testSiteActions(self):
        installed = [(a.getId(), a.getCategory()) for a in self.actions.listActions()]
        self.failUnless(('sitemap', 'site_actions') in installed)
        self.failUnless(('contact', 'site_actions') in installed)
        self.failUnless(('accessibility', 'site_actions') in installed)
        self.failUnless(('plone_setup', 'site_actions') in installed)

    def testNoMembershipToolPloneSetupAction(self):
        installed = [a.getId() for a in self.membership.listActions()]
        self.failIf('plone_setup' in installed)

    def testTypesHaveSelectedLayoutViewAction(self):
        # Should add method aliases to the Plone Site FTI
        types = ('Document', 'Event', 'Favorite', 'File', 'Folder', 'Image', 'Link', 'News Item', 'Topic', 'Plone Site')
        for typeName in types:
            fti = getattr(self.types, typeName)
            aliases = fti.getMethodAliases()
            self.assertEqual(aliases['view'], '(selected layout)')

    def testPortalUsesMethodAliases(self):
        fti = self.portal.getTypeInfo()
        for action in fti.listActions():
            if action.getId() == 'edit':
                self.assertEqual(action.getActionExpression(), 'string:${object_url}/edit')
            if action.getId() == 'sharing':
                self.assertEqual(action.getActionExpression(), 'string:${object_url}/sharing')

    def testNavigationSettingsActionIcon(self):
        # There should be a NavigationSettings action icon
        for icon in self.icons.listActionIcons():
            if icon.getActionId() == 'NavigationSettings':
                break
        else:
            self.fail("Action icons tool has no 'NavigationSettings' icon")

    def testNavigationAndSearchPanelsInstalled(self):
        # Navigation and search panels should be installed
        haveSearch = False
        haveNavigation = False
        for panel in self.cp.listActions():
            if panel.getId() == 'SearchSettings':
                haveSearch = True
            elif panel.getId() == 'NavigationSettings':
                haveNavigation = True
        self.failUnless(haveSearch and haveNavigation)

    def testOwnerHasAccessInactivePermission(self):
        permission_on_role = [p for p in self.portal.permissionsOfRole('Owner')
            if p['name'] == CMFCorePermissions.AccessInactivePortalContent][0]
        self.failUnless(permission_on_role['selected'])
        cur_perms = self.portal.permission_settings(
                            CMFCorePermissions.AccessInactivePortalContent)[0]
        self.failUnless(cur_perms['acquire'])

    def testSyndicationEnabledByDefault(self):
        syn = self.portal.portal_syndication
        self.failUnless(syn.isSiteSyndicationAllowed())

    def testSyndicationEnabledOnNewsAndEvents(self):
        syn = self.portal.portal_syndication
        self.failUnless(syn.isSyndicationAllowed(self.portal.news))
        self.failUnless(syn.isSyndicationAllowed(self.portal.events))

    def testSyndicationTabDisabled(self):
        # Syndication tab should be disabled by default
        for action in self.portal.portal_syndication.listActions():
            if action.getId() == 'syndication' and action.visible:
                self.fail("Actions tool still has visible 'syndication' action")

    def testObjectButtonActionsInvisibleOnPortalRoot(self):
        # only a manager would have proper permissions
        self.setRoles(['Manager', 'Member'])
        acts = self.actions.listFilteredActionsFor(self.portal)
        self.failIf(acts.has_key('object_buttons'))

    def testObjectButtonActionsInvisibleOnPortalDefaultDocument(self):
        # only a manager would have proper permissions
        self.setRoles(['Manager', 'Member'])
        self.portal.invokeFactory('Document','index_html')
        acts = self.actions.listFilteredActionsFor(self.portal.index_html)
        self.failIf(acts.has_key('object_buttons'))

    def testObjectButtonActionsOnDefaultDocumentApplyToParent(self):
        # only a manager would have proper permissions
        self.setRoles(['Manager', 'Member'])
        self.folder.invokeFactory('Document','index_html')
        acts = self.actions.listFilteredActionsFor(self.folder.index_html)
        buttons = acts['object_buttons']
        self.assertEqual(len(buttons), 3)
        urls = [a['url'] for a in buttons]
        for url in urls:
            self.failIf('index_html' in url, 'Action wrongly applied to default page object %s'%url)

    def testObjectButtonActionsPerformCorrectAction(self):
        # only a manager would have proper permissions
        self.setRoles(['Manager', 'Member'])
        self.folder.invokeFactory('Document','index_html')
        acts = self.actions.listFilteredActionsFor(self.folder.index_html)
        buttons = acts['object_buttons']
        self.assertEqual(len(buttons), 3)
        urls = [(a['id'],a['url']) for a in buttons]
        for url in urls:
            # ensure that e.g. the 'copy' url contains object_copy
            self.failUnless('object_'+url[0] in url[1], "%s does not perform the expected object_%s action"%(url[0],url[0]))

    def testObjectButtonActionsInExpectedOrder(self):
        # The object buttons need to be in a standardized order
        self.setRoles(['Manager', 'Member'])
        # fill the copy buffer so we see all actions
        self.folder.cb_dataValid = True
        acts = self.actions.listFilteredActionsFor(self.folder)
        buttons = acts['object_buttons']
        self.assertEqual(len(buttons),4)
        ids = [(a['id']) for a in buttons]
        self.assertEqual(ids, ['cut','copy','paste','delete'])

    def testPortalSharingActionIsLocalRoles(self):
        fti = getattr(self.types, 'Plone Site')
        haveSharing = False
        haveLocalRoles = False
        for a in fti.listActions():
            if a.getId() == 'sharing':
                haveSharing = True
            elif a.getId() == 'local_roles':
                haveLocalRoles = True
        self.failIf(haveSharing)
        self.failUnless(haveLocalRoles)

    def testPlone3rdPartyLayerInDefault(self):
        # plone_3rdParty layer should exist
        path = self.skins.getSkinPath('Plone Default')
        self.failUnless('plone_3rdParty' in path)

    def testPlone3rdPartyLayerInTableless(self):
        # plone_3rdParty layer should exist
        path = self.skins.getSkinPath('Plone Tableless')
        self.failUnless('plone_3rdParty' in path)

    def testPloneLoginLayerInDefault(self):
        # plone_login layer should exist
        path = self.skins.getSkinPath('Plone Default')
        self.failUnless('plone_login' in path)

    def testPloneLoginLayerInTableless(self):
        # plone_login layer should exist
        path = self.skins.getSkinPath('Plone Tableless')
        self.failUnless('plone_login' in path)

    def testCMFLegacySkinComesLastInDefault(self):
        # cmf_legacy should be the last skin layer
        path = self.skins.getSkinPath('Plone Default')
        path = [x.strip() for x in path.split(',')]
        self.assertEqual(path[-1], 'cmf_legacy')

    def testCMFLegacySkinComesLastInTableless(self):
        # cmf_legacy should be the last skin layer
        path = self.skins.getSkinPath('Plone Tableless')
        path = [x.strip() for x in path.split(',')]
        self.assertEqual(path[-1], 'cmf_legacy')

    def testMemberHasViewGroupsPermission(self):
        # Member should be granted the 'View Groups' permission
        member_has_permission = [p for p in
                self.portal.permissionsOfRole('Member')
                                        if p['name'] == 'View Groups'][0]
        self.failUnless(member_has_permission['selected'])


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
