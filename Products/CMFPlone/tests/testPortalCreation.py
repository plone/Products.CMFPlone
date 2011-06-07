#
# Tests portal creation
#

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy
from Products.CMFCore.tests.base.testcase import WarningInterceptor

from zope.component import getGlobalSiteManager
from zope.component import getSiteManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.interfaces import IComponentLookup
from zope.component.interfaces import IComponentRegistry
from zope.location.interfaces import ISite
from zope.site.hooks import setSite, clearSite

from Acquisition import aq_base
from DateTime import DateTime

from Products.CMFCore.CachingPolicyManager import CachingPolicyManager
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import setuphandlers
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.UnicodeSplitter import Splitter, CaseNormalizer
from Products.GenericSetup.browser.manage import ExportStepsView
from Products.GenericSetup.browser.manage import ImportStepsView

from Products.StandardCacheManagers.AcceleratedHTTPCacheManager import \
     AcceleratedHTTPCacheManager
from Products.StandardCacheManagers.RAMCacheManager import \
     RAMCacheManager

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY as CONTEXT_PORTLETS


class TestPortalCreation(PloneTestCase.PloneTestCase, WarningInterceptor):

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
        self.skins = self.portal.portal_skins
        self.transforms = self.portal.portal_transforms
        self.javascripts = self.portal.portal_javascripts
        self.setup = self.portal.portal_setup

    def beforeTearDown(self):
        self._free_warning_output()

    def testInstanceVersion(self):
        # Test if the version of the instance has been set
        mt = getToolByName(self.portal, 'portal_migration')
        self.assertEqual(mt._version, False)

    def testProfileVersion(self):
        # The profile version for the base profile should be the same
        # as the file system version and the instance version
        mt = getToolByName(self.portal, 'portal_migration')
        setup = getToolByName(self.portal, 'portal_setup')

        version = setup.getVersionForProfile(_DEFAULT_PROFILE)
        instance = mt.getInstanceVersion()
        fsversion = mt.getFileSystemVersion()
        self.assertEqual(instance, fsversion)
        self.assertEqual(instance, version)

    def testPloneSkins(self):
        # Plone skins should have been set up
        self.failUnless(hasattr(self.folder, 'plone_powered.gif'))

    def testDefaultSkin(self):
        # index_html should render
        self.portal.index_html()

    def testNoIndexHtmlDocument(self):
        # The portal should not contain an index_html Document
        self.failIf('index_html' in self.portal)

    def testCanViewManagementScreen(self):
        # Make sure the ZMI management screen works
        self.portal.manage_main()

    def testWorkflowIsActionProvider(self):
        # The workflow tool is one of the last remaining action providers.
        self.failUnless('portal_workflow' in self.actions.listActionProviders())

    def testMembersFolderMetaType(self):
        # Members folder should have meta_type 'ATFolder'
        members = self.membership.getMembersFolder()
        self.assertEqual(members.meta_type, 'ATFolder')

    def testMembersFolderPortalType(self):
        # Members folder should have portal_type 'Folder'
        members = self.membership.getMembersFolder()
        self.assertEqual(members._getPortalTypeName(), 'Folder')

    def testMembersFolderMeta(self):
        # Members folder should have title 'Users'
        members = self.membership.getMembersFolder()
        self.assertEqual(members.getId(), 'Members')
        self.assertEqual(members.Title(), 'Users')

    def testMembersFolderIsIndexed(self):
        # Members folder should be cataloged
        res = self.catalog(getId='Members')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'Members')
        self.assertEqual(res[0].Title, 'Users')

    def testMembersFolderOrdering(self):
        # Members folder should not have explicit ordering
        members = self.membership.getMembersFolder()
        self.assertEqual(members._ordering, 'unordered')

    def testMailHost(self):
        # MailHost should be of the standard variety
        mailhost = self.portal.MailHost
        self.assertEqual(mailhost.meta_type, 'Mail Host')

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

    def testFolderHasFolderListingAction(self):
        # Folders should have a 'folderlisting' action
        folder = self.types.getTypeInfo('Folder')
        for action in folder._cloneActions():
            if action.id == 'folderlisting':
                break
        else:
            self.fail("Folder has no 'folderlisting' action")

    def testImagePatch(self):
        # Is it ok to remove the imagePatch? Probably not as we
        # don't want the border attribute ...
        self.folder.invokeFactory('Image', id='foo', file=dummy.Image())
        endswith = ' alt="" title="" height="16" width="16" />'
        self.assertEqual(self.folder.foo.tag()[-len(endswith):], endswith)

    def testNoPortalFormTool(self):
        # portal_form should have been removed
        self.failIf('portal_form' in self.portal)

    def testNoPortalNavigationTool(self):
        # portal_navigation should have been removed
        self.failIf('portal_navigation' in self.portal)

    def testNoFormProperties(self):
        # form_properties should have been removed
        self.failIf('form_properties' in self.properties)

    def testNoNavigationProperties(self):
        # navigation_properties should have been removed
        self.failIf('navigation_properties' in self.properties)

    def testFullScreenAction(self):
        # There should be a full_screen action
        self.failUnless(self.actions.getActionInfo('document_actions/full_screen') is not None)
        action = self.actions.getActionInfo('document_actions/full_screen')
        self.failUnless('fullscreenexpand_icon' in action['icon'])

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
        self.failUnless(hasattr(self.portal, 'portal_kss'))
        self.failUnless(hasattr(self.portal, 'portal_javascripts'))

    def testUnfriendlyTypesProperty(self):
        # We should have an types_not_searched property
        self.failUnless(self.properties.site_properties.hasProperty('types_not_searched'))
        self.failUnless('Plone Site' in self.properties.site_properties.getProperty('types_not_searched'))

    def testNonDefaultPageTypes(self):
        # We should have a default_page_types property
        self.failUnless(self.properties.site_properties.hasProperty('default_page_types'))
        self.failUnless('Folder' not in self.properties.site_properties.getProperty('default_page_types'))
        self.failUnless('Topic' in self.properties.site_properties.getProperty('default_page_types'))

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

    def testNewsTopicIsIndexed(self):
        # News (smart) folder should be cataloged
        res = self.catalog(path={'query' : '/plone/news/aggregator', 'depth' : 0})
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'aggregator')
        self.assertEqual(res[0].Title, 'News')
        self.assertEqual(res[0].Description, 'Site News')

    def testEventsTopicIsIndexed(self):
        # Events (smart) folder should be cataloged
        res = self.catalog(path={'query' : '/plone/events/aggregator', 'depth' : 0})
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'aggregator')
        self.assertEqual(res[0].Title, 'Events')
        self.assertEqual(res[0].Description, 'Site Events')

    def testNewsFolderIsIndexed(self):
        # News folder should be cataloged
        res = self.catalog(path={'query' : '/plone/news', 'depth' : 0})
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'news')
        self.assertEqual(res[0].Title, 'News')
        self.assertEqual(res[0].Description, 'Site News')

    def testEventsFolderIsIndexed(self):
        # Events folder should be cataloged
        res = self.catalog(path={'query' : '/plone/events', 'depth' : 0})
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'events')
        self.assertEqual(res[0].Title, 'Events')
        self.assertEqual(res[0].Description, 'Site Events')

    def testNewsFolder(self):
        self.failUnless('news' in self.portal.objectIds())
        folder = getattr(self.portal, 'news')
        self.assertEqual(folder.portal_type, 'Folder')
        self.assertEqual(folder._ordering, 'unordered')
        self.assertEqual(folder.getDefaultPage(), 'aggregator')
        self.assertEqual(folder.getRawLocallyAllowedTypes(), ('News Item',))
        self.assertEqual(folder.getRawImmediatelyAddableTypes(), ('News Item',))
        self.assertEqual(folder.checkCreationFlag(), False)

    def testEventsFolder(self):
        self.failUnless('events' in self.portal.objectIds())
        folder = getattr(self.portal, 'events')
        self.assertEqual(folder.portal_type, 'Folder')
        self.assertEqual(folder._ordering, 'unordered')
        self.assertEqual(folder.getDefaultPage(), 'aggregator')
        self.assertEqual(folder.getRawLocallyAllowedTypes(), ('Event',))
        self.assertEqual(folder.getRawImmediatelyAddableTypes(), ('Event',))
        self.assertEqual(folder.checkCreationFlag(), False)

    def testNewsTopic(self):
        # News topic is in place as default view and has a criterion to show
        # only News Items, and uses the folder_summary_view.
        self.assertEqual(['aggregator'], [i for i in self.portal.news.objectIds()])
        topic = getattr(self.portal.news, 'aggregator')
        self.assertEqual(topic._getPortalTypeName(), 'Topic')
        self.assertEqual(topic.buildQuery()['Type'], ('News Item',))
        self.assertEqual(topic.buildQuery()['review_state'], 'published')
        self.assertEqual(topic.getLayout(), 'folder_summary_view')
        self.assertEqual(topic.checkCreationFlag(), False)

    def testEventsTopic(self):
        # Events topic is in place as default view and has criterion to show
        # only future Events Items.
        self.assertEqual(['aggregator'], [i for i in self.portal.events.objectIds()])
        topic = getattr(self.portal.events, 'aggregator')
        self.assertEqual(topic._getPortalTypeName(), 'Topic')
        query = topic.buildQuery()
        self.assertEqual(query['Type'], ('Event',))
        self.assertEqual(query['review_state'], 'published')
        self.assertEqual(query['start']['query'].Date(), DateTime().Date())
        self.assertEqual(query['start']['range'], 'min')
        self.assertEqual(topic.checkCreationFlag(), False)

    def testObjectButtonActions(self):
        self.setRoles(['Manager', 'Member'])
        atool = self.actions
        self.failIf(atool.getActionInfo('object_buttons/cut') is None)
        self.failIf(atool.getActionInfo('object_buttons/copy') is None)
        self.failIf(atool.getActionInfo('object_buttons/paste') is None)
        self.failIf(atool.getActionInfo('object_buttons/delete') is None)

    def testContentsTabVisible(self):
        for a in self.actions.listActions():
            if a.getId() == 'folderContents':
                self.failUnless(a.visible)

    def testDefaultGroupsAdded(self):
        self._trap_warning_output()
        self.failUnless('Administrators' in self.groups.listGroupIds())
        self.failUnless('Reviewers' in self.groups.listGroupIds())

    def testDefaultTypesInPortalFactory(self):
        types = self.factory.getFactoryTypes().keys()
        for metaType in ('Document', 'Event', 'File', 'Folder', 'Image',
                         'Folder', 'Link', 'News Item',
                         'Topic'):
            self.failUnless(metaType in types)

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
        actions = self.actions['folder_buttons']
        self.assertEqual(actions.values()[-1].id, 'change_state')

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
        self.assertEqual(self.types['Folder'].getActionObject('folder/folderlisting').getActionExpression(),
                         'string:${folder_url}/view')

    def testEnableLivesearchProperty(self):
        # site_properties should have enable_livesearch property
        self.failUnless(self.properties.site_properties.hasProperty('enable_livesearch'))

    def testRedirectLinksProperty(self):
        self.failUnless(self.properties.site_properties.hasProperty('redirect_links'))
        self.assertEquals(True, self.properties.site_properties.redirect_links)

    def testLinkDefaultView(self):
        self.assertEqual(self.types.Link.default_view, 'link_redirect_view')

    def testTTWLockableProperty(self):
        self.failUnless(self.properties.site_properties.hasProperty('lock_on_ttw_edit'))
        self.assertEquals(True, self.properties.site_properties.lock_on_ttw_edit)

    def testPortalFTIIsDynamicFTI(self):
        # Plone Site FTI should be a DynamicView FTI
        fti = self.portal.getTypeInfo()
        self.assertEqual(fti.meta_type, 'Factory-based Type Information with dynamic views')

    def testPloneSiteFTIHasMethodAliases(self):
        # Should add method aliases to the Plone Site FTI
        expected_aliases = {
                '(Default)'  : '(dynamic view)',
                'view'       : '(selected layout)',
                'edit'       : '@@site-controlpanel',
                'sharing'    : '@@sharing',
              }
        fti = self.portal.getTypeInfo()
        aliases = fti.getMethodAliases()
        self.assertEqual(aliases, expected_aliases)

    def testSiteActions(self):
        self.setRoles(['Manager', 'Member'])
        atool = self.actions
        self.failIf(atool.getActionInfo('site_actions/sitemap') is None)
        self.failIf(atool.getActionInfo('site_actions/contact') is None)
        self.failIf(atool.getActionInfo('site_actions/accessibility') is None)

    def testSetupAction(self):
        self.setRoles(['Manager', 'Member'])
        atool = self.actions
        self.failIf(atool.getActionInfo('user/plone_setup') is None)
        self.failIf(atool.getActionInfo('site_actions/plone_setup') is None)

    def testTypesHaveSelectedLayoutViewAction(self):
        # Should add method aliases to the Plone Site FTI
        types = ('Document', 'Event', 'File', 'Folder', 'Image', 'Link', 'News Item', 'Topic', 'Plone Site')
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
            if p['name'] == AccessInactivePortalContent][0]
        self.failUnless(permission_on_role['selected'])
        cur_perms = self.portal.permission_settings(
                            AccessInactivePortalContent)[0]
        self.failUnless(cur_perms['acquire'])

    def testSyndicationEnabledByDefault(self):
        syn = self.portal.portal_syndication
        self.failUnless(syn.isSiteSyndicationAllowed())

    def testSyndicationEnabledOnNewsAndEvents(self):
        syn = self.portal.portal_syndication
        self.failUnless(syn.isSyndicationAllowed(self.portal.news.aggregator))
        self.failUnless(syn.isSyndicationAllowed(self.portal.events.aggregator))

    def testSyndicationTabDisabled(self):
        # Syndication tab should be disabled by default
        for action in self.actions.listActions():
            if action.getId() == 'syndication' and action.visible:
                self.fail("Actions tool still has visible 'syndication' action")

    def testObjectButtonActionsInvisibleOnPortalRoot(self):
        # only a manager would have proper permissions
        self.setRoles(['Manager', 'Member'])
        acts = self.actions.listFilteredActionsFor(self.portal)
        buttons = acts.get('object_buttons',[])
        self.assertEquals(0, len(buttons))

    def testObjectButtonActionsInvisibleOnPortalDefaultDocument(self):
        # only a manager would have proper permissions
        self.setRoles(['Manager', 'Member'])
        self.portal.invokeFactory('Document','index_html')
        acts = self.actions.listFilteredActionsFor(self.portal.index_html)
        buttons = acts.get('object_buttons', [])
        self.assertEquals(0, len(buttons))

    def testObjectButtonActionsOnDefaultDocumentDoNotApplyToParent(self):
        # only a manager would have proper permissions
        self.setRoles(['Manager', 'Member'])
        self.folder.invokeFactory('Document','index_html')
        acts = self.actions.listFilteredActionsFor(self.folder.index_html)
        buttons = acts['object_buttons']
        self.assertEqual(len(buttons), 4)
        urls = [a['url'] for a in buttons]
        for url in urls:
            self.failIf('index_html' not in url, 'Action wrongly applied to parent object %s'%url)

    def testObjectButtonActionsPerformCorrectAction(self):
        # only a manager would have proper permissions
        self.setRoles(['Manager', 'Member'])
        self.folder.invokeFactory('Document','index_html')
        acts = self.actions.listFilteredActionsFor(self.folder.index_html)
        buttons = acts['object_buttons']
        self.assertEqual(len(buttons), 4)
        # special case for delete which needs a confirmation form
        urls = [(a['id'],a['url']) for a in buttons
                if a['id'] not in ('delete',)]
        for url in urls:
            # ensure that e.g. the 'copy' url contains object_copy
            self.failUnless('object_'+url[0] in url[1], "%s does not perform the expected object_%s action"%(url[0],url[0]))

        delete_action = [(a['id'],a['url']) for a in buttons
                if a['id'] == 'delete'][0]
        self.failUnless('delete_confirmation' in delete_action[1],
                         "object_delete does not use the confirmation form")

    def testObjectButtonActionsInExpectedOrder(self):
        # The object buttons need to be in a standardized order
        self.setRoles(['Manager', 'Member'])
        # fill the copy buffer so we see all actions
        self.folder.cb_dataValid = True
        acts = self.actions.listFilteredActionsFor(self.folder)
        buttons = acts['object_buttons']
        self.assertEqual(len(buttons),5)
        ids = [(a['id']) for a in buttons]
        self.assertEqual(ids, ['cut','copy','paste','delete', 'rename',])

    def testPlone3rdPartyLayerInDefault(self):
        # plone_3rdParty layer should exist
        path = self.skins.getSkinPath('Plone Default')
        self.failUnless('plone_3rdParty' in path)

    def testPloneLoginLayerInDefault(self):
        # plone_login layer should exist
        path = self.skins.getSkinPath('Plone Default')
        self.failUnless('plone_login' in path)

    def testCMFLegacySkinComesLastInDefault(self):
        # cmf_legacy should be the last skin layer
        path = self.skins.getSkinPath('Plone Default')
        path = [x.strip() for x in path.split(',')]
        self.assertEqual(path[-1], 'cmf_legacy')

    def testCustomSkinFolderExists(self):
        # the custom skin needs to be created
        self.failUnless('custom' in self.skins)

    def testCustomSkinFolderComesFirst(self):
        firstInDefaultSkin = (
            self.skins.getSkinPath('Plone Default').split(',')[0])
        self.assertEqual(
            firstInDefaultSkin, 'custom',
            "The 'custom' layer was not the first in the Plone Default skin. "
            "It was %r." % firstInDefaultSkin)

    def testMemberHasViewGroupsPermission(self):
        # Member should be granted the 'View Groups' permission
        member_has_permission = [p for p in
                self.portal.permissionsOfRole('Member')
                                        if p['name'] == 'View Groups'][0]
        self.failUnless(member_has_permission['selected'])

    def testDiscussionItemWorkflow(self):
        # By default the discussion item has the one_state_workflow
        self.assertEqual(self.workflow.getChainForPortalType('Discussion Item'), 
                         ('one_state_workflow',))

    def testFolderHasFolderListingView(self):
        # Folder type should allow 'folder_listing'
        self.failUnless('folder_listing' in self.types.Folder.view_methods)

    def testFolderHasSummaryView(self):
        # Folder type should allow 'folder_summary_view'
        self.failUnless('folder_summary_view' in self.types.Folder.view_methods)

    def testFolderHasTabularView(self):
        # Folder type should allow 'folder_tabular_view'
        self.failUnless('folder_tabular_view' in self.types.Folder.view_methods)

    def testFolderHasAlbumView(self):
        # Folder type should allow 'atct_album_view'
        self.failUnless('atct_album_view' in self.types.Folder.view_methods)

    def testConfigurableSafeHtmlTransform(self):
        # The safe_html transformation should be configurable
        try:
            self.transforms.safe_html.get_parameter_value('disable_transform')
        except (AttributeError, KeyError):
            self.fail('safe_html transformation not updated')

    def testNavtreePropertiesNormalized(self):
        ntp = self.portal.portal_properties.navtree_properties
        toRemove = ['skipIndex_html', 'showMyUserFolderOnly', 'showFolderishSiblingsOnly',
                    'showFolderishChildrenOnly', 'showNonFolderishObject', 'showTopicResults',
                    'rolesSeeContentView', 'rolesSeeUnpublishedContent', 'rolesSeeContentsView ',
                    'batchSize', 'sortCriteria', 'croppingLength', 'forceParentsInBatch',
                    'rolesSeeHiddenContent', 'typesLinkToFolderContents']
        toAdd = {'name' : '', 'root' : '/', 'currentFolderOnlyInNavtree' : False}
        for property in toRemove:
            self.assertEqual(ntp.getProperty(property, None), None)
        for property, value in toAdd.items():
            self.assertEqual(ntp.getProperty(property), value)
        self.assertEqual(ntp.getProperty('bottomLevel'), 0)

    def testvcXMLRPCRemoved(self):
        # vcXMLRPC.js should no longer be registered
        self.failIf('vcXMLRPC.js' in self.javascripts.getResourceIds())

    def testCacheManagers(self):
        # The cache and caching policy managers should exist
        httpcache = self.portal._getOb('HTTPCache', None)
        ramcache = self.portal._getOb('RAMCache', None)
        cpm = self.portal._getOb('caching_policy_manager', None)
        self.failUnless(isinstance(httpcache, AcceleratedHTTPCacheManager))
        self.failUnless(isinstance(ramcache, RAMCacheManager))
        self.failUnless(isinstance(cpm, CachingPolicyManager))

    def testHomeActionUsesView(self):
        actions = self.actions.listActions()
        homeAction = [x for x in actions if x.id == 'index_html'][0]
        self.assertEquals(homeAction.getInfoData()[0]['url'].text, 'string:${globals_view/navigationRootUrl}')

    def testPloneLexicon(self):
        # Plone lexicon should use new splitter and case normalizer
        pipeline = self.catalog.plone_lexicon._pipeline
        self.failUnless(len(pipeline) >= 2)
        self.failUnless(isinstance(pipeline[0], Splitter))
        self.failUnless(isinstance(pipeline[1], CaseNormalizer))

    def testMakeSnapshot(self):
        # GenericSetup snapshot should work
        self.setRoles(['Manager'])
        snapshot_id = self.setup._mangleTimestampName('test')
        self.setup.createSnapshot(snapshot_id)

    def testValidateEmail(self):
        # validate_email should be on by default
        self.failUnless(self.portal.getProperty('validate_email'))

    def testSiteManagerSetup(self):
        clearSite()
        # The portal should be an ISite
        self.failUnless(ISite.providedBy(self.portal))
        # There should be a IComponentRegistry
        comp = IComponentLookup(self.portal)
        IComponentRegistry.providedBy(comp)

        # Test if we get the right site managers
        gsm = getGlobalSiteManager()
        sm = getSiteManager()
        # Without setting the site we should get the global site manager
        self.failUnless(sm is gsm)

        # Now we set the site, as it is done in url traversal normally
        setSite(self.portal)
        # And should get the local site manager
        sm = getSiteManager()
        self.failUnless(aq_base(sm) is aq_base(comp))

    def testUtilityRegistration(self):
        gsm = getGlobalSiteManager()
        global_util = dummy.DummyUtility()

        # Register a global utility and see if we can get it
        gsm.registerUtility(global_util, dummy.IDummyUtility)
        getutil = getUtility(dummy.IDummyUtility)
        self.assertEquals(getutil, global_util)

        # Register a local utility and see if we can get it
        sm = getSiteManager()
        local_util = dummy.DummyUtility()

        sm.registerUtility(local_util, dummy.IDummyUtility)
        getutil = getUtility(dummy.IDummyUtility)
        self.assertEquals(getutil, local_util)
        # Clean up the site again
        clearSite()

        # Without a site we get the global utility
        getutil = getUtility(dummy.IDummyUtility)
        self.assertEquals(getutil, global_util)

        # Clean up again and unregister the utilites
        gsm.unregisterUtility(provided=dummy.IDummyUtility)
        sm.unregisterUtility(provided=dummy.IDummyUtility)

        # Make sure unregistration was successful
        util = queryUtility(dummy.IDummyUtility)
        self.failUnless(util is None)

    def testPortletManagersInstalled(self):
        sm = getSiteManager(self.portal)
        registrations = [r.name for r in sm.registeredUtilities()
                            if IPortletManager == r.provided]
        self.assertEquals(['plone.dashboard1', 'plone.dashboard2', 'plone.dashboard3', 'plone.dashboard4',
                            'plone.leftcolumn', 'plone.rightcolumn'], sorted(registrations))

    def testPortletAssignmentsAtRoot(self):
        leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn')
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn')

        left = getMultiAdapter((self.portal, leftColumn,), IPortletAssignmentMapping)
        right = getMultiAdapter((self.portal, rightColumn,), IPortletAssignmentMapping)

        self.assertEquals(len(left), 1)
        self.assertEquals(len(right), 2)

    def testPortletBlockingForMembersFolder(self):
        members = self.portal.Members
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn')
        portletAssignments = getMultiAdapter((members, rightColumn,), ILocalPortletAssignmentManager)
        self.assertEquals(True, portletAssignments.getBlacklistStatus(CONTEXT_PORTLETS))

    def testAddablePortletsInColumns(self):
        for name in (u'plone.leftcolumn', u'plone.rightcolumn'):
            column = getUtility(IPortletManager, name=name)
            addable_types = [
              p.addview for p in column.getAddablePortletTypes()
              ]
            addable_types.sort()
            self.assertEqual([
                'plone.portlet.collection.Collection',
                'plone.portlet.static.Static',
                'portlets.Calendar',
                'portlets.Classic',
                'portlets.Events',
                'portlets.Login',
                'portlets.Navigation',
                'portlets.News',
                'portlets.Recent',
                'portlets.Review',
                'portlets.Search',
                'portlets.rss'], addable_types)

    def testAddablePortletsInDashboard(self):
        for name in ('plone.dashboard1', 'plone.dashboard2',
          'plone.dashboard3', 'plone.dashboard4'):
            column = getUtility(IPortletManager, name=name)
            addable_types = [
              p.addview for p in column.getAddablePortletTypes()
              ]
            addable_types.sort()
            self.assertEqual([
              'plone.portlet.collection.Collection',
              'plone.portlet.static.Static',
              'portlets.Calendar',
              'portlets.Classic',
              'portlets.Events',
              'portlets.News',
              'portlets.Recent',
              'portlets.Review',
              'portlets.Search',
              'portlets.rss'
              ], addable_types)

    def testReaderEditorRoles(self):
        self.failUnless('Reader' in self.portal.valid_roles())
        self.failUnless('Editor' in self.portal.valid_roles())
        self.failUnless('Reader' in self.portal.acl_users.portal_role_manager.listRoleIds())
        self.failUnless('Editor' in self.portal.acl_users.portal_role_manager.listRoleIds())
        self.failUnless('View' in [r['name'] for r in self.portal.permissionsOfRole('Reader') if r['selected']])
        self.failUnless('Modify portal content' in [r['name'] for r in self.portal.permissionsOfRole('Editor') if r['selected']])

    def testWorkflowsInstalled(self):
        for wf in ['intranet_workflow', 'intranet_folder_workflow',
                'one_state_workflow', 'simple_publication_workflow']:
            self.failUnless(wf in self.portal.portal_workflow)

    def testAddPermisssionsGivenToContributorRole(self):
        self.failUnless('Contributor' in self.portal.valid_roles())
        self.failUnless('Contributor' in self.portal.acl_users.portal_role_manager.listRoleIds())
        for p in ['Add portal content', 'Add portal folders', 'ATContentTypes: Add Document',
                    'ATContentTypes: Add Event',
                    'ATContentTypes: Add File', 'ATContentTypes: Add Folder',
                    'ATContentTypes: Add Link', 'ATContentTypes: Add News Item', ]:
            self.failUnless(p in [r['name'] for r in
                                self.portal.permissionsOfRole('Contributor') if r['selected']])

    def testSharingAction(self):
        # Should be in portal_actions
        self.failUnless('local_roles' in self.actions.object)

        # Should not be in any of the default FTIs
        for fti in self.types.values():
            self.failIf('local_roles' in [a.id for a in fti.listActions()])

    def testSecondaryEditorPermissionsGivenToEditorRole(self):
        for p in ['Manage properties', 'Modify view template', 'Request review']:
            self.failUnless(p in [r['name'] for r in
                                self.portal.permissionsOfRole('Editor') if r['selected']])

    def testNonFolderishTabsProperty(self):
        self.assertEquals(False, self.properties.site_properties.disable_nonfolderish_sections)

    def testPortalContentLanguage(self):
        from zope.component import provideUtility
        from zope.i18n.interfaces import ITranslationDomain
        from zope.i18n.simpletranslationdomain import SimpleTranslationDomain

        # Let's fake the news title translations
        messages = {
            ('de', u'news-title'): u'Foo',
            ('pt_BR', u'news-title'): u'Bar',
        }
        pfp = SimpleTranslationDomain('plonefrontpage', messages)
        provideUtility(pfp, ITranslationDomain, name='plonefrontpage')

        # Setup the new placeholder folders
        self.folder.invokeFactory('Folder', 'brazilian')
        self.folder.invokeFactory('Folder', 'german')

        # Check if the content is being created in German
        self.folder.german.setLanguage('de')
        self.loginAsPortalOwner()
        setuphandlers.setupPortalContent(self.folder.german)
        self.failUnlessEqual(self.folder.german.news.Title(), 'Foo')

        # Check if the content is being created in a composite
        # language code, in this case Brazilian Portuguese
        self.folder.brazilian.setLanguage('pt-br')
        setuphandlers.setupPortalContent(self.folder.brazilian)
        self.failUnlessEqual(self.folder.brazilian.news.Title(), 'Bar')

    def testNoDoubleGenericSetupImportSteps(self):
        view=ImportStepsView(self.setup, None)
        self.assertEqual([i['id'] for i in view.doubleSteps()], [])

    def testNoInvalidGenericSetupImportSteps(self):
        view=ImportStepsView(self.setup, None)
        self.assertEqual([i['id'] for i in view.invalidSteps()], [])

    def testNoDoubleGenericSetupExportSteps(self):
        view=ExportStepsView(self.setup, None)
        self.assertEqual([i['id'] for i in view.doubleSteps()], [])

    def testNoInvalidGenericSetupExportSteps(self):
        view=ExportStepsView(self.setup, None)
        self.assertEqual([i['id'] for i in view.invalidSteps()], [])


class TestPortalBugs(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.members = self.membership.getMembersFolder()
        self.catalog = self.portal.portal_catalog
        self.mem_index_type = "Script (Python)"
        self.setupAuthenticator()

    def testMembersIndexHtml(self):
        # index_html for Members folder should be a Page Template
        members = self.members
        self.assertEqual(aq_base(members).meta_type, 'ATFolder')
        self.failUnless(hasattr(aq_base(members), 'index_html'))
        # getitem works
        self.assertEqual(aq_base(members)['index_html'].meta_type, self.mem_index_type)
        self.assertEqual(members['index_html'].meta_type, self.mem_index_type)
        # _getOb works
        self.assertEqual(aq_base(members)._getOb('index_html').meta_type, self.mem_index_type)
        self.assertEqual(members._getOb('index_html').meta_type, self.mem_index_type)
        # getattr works when called explicitly
        self.assertEqual(aq_base(members).__getattr__('index_html').meta_type, self.mem_index_type)
        self.assertEqual(members.__getattr__('index_html').meta_type, self.mem_index_type)

    def testLargePloneFolderHickup(self):
        # Attribute access for 'index_html' acquired the Document from the
        # portal instead of returning the local Page Template. This was due to
        # special treatment of 'index_html' in the PloneFolder base class and
        # got fixed by hazmat.
        members = self.members
        self.assertEqual(aq_base(members).meta_type, 'ATFolder')
        self.assertEqual(members.index_html.meta_type, self.mem_index_type)

    def testSubsequentProfileImportSucceeds(self):
        # Subsequent profile imports fail (#5439)
        self.loginAsPortalOwner()
        setup_tool = getToolByName(self.portal, "portal_setup")
        # this will raise an error if it fails
        profile = setup_tool.getBaselineContextID()
        setup_tool.runAllImportStepsFromProfile(profile, purge_old=True)
        self.failUnless(1 == 1)

    def testFinalStepsWithMembersFolderDeleted(self):
        # We want the final steps to work even if the 'Members' folder
        # is gone
        self.loginAsPortalOwner()
        portal = self.portal
        portal.manage_delObjects(['Members'])
        class FakeContext:
            def getSite(self):
                return portal
            def readDataFile(self, filename):
                return True # Anything other than None runs the step

        setuphandlers.importFinalSteps(FakeContext()) # raises error if fail
        self.failUnless(1 == 1)


class TestManagementPageCharset(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.properties = self.portal.portal_properties

    def testManagementPageCharset(self):
        manage_charset = getattr(self.portal, 'management_page_charset', None)
        self.failUnless(manage_charset)
        self.assertEqual(manage_charset, 'utf-8')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortalCreation))
    suite.addTest(makeSuite(TestPortalBugs))
    suite.addTest(makeSuite(TestManagementPageCharset))
    return suite
