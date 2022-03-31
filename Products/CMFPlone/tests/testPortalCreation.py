from Acquisition import aq_base
from plone.portlets.constants import CONTEXT_CATEGORY as CONTEXT_PORTLETS
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.protect import createToken
from plone.registry.interfaces import IRegistry
from Products.CMFCore.CachingPolicyManager import CachingPolicyManager
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import setuphandlers
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.interfaces import IFilterSchema
from Products.CMFPlone.interfaces import INavigationSchema
from Products.CMFPlone.interfaces import ISearchSchema
from Products.CMFPlone.tests import dummy
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.UnicodeSplitter import I18NNormalizer
from Products.CMFPlone.UnicodeSplitter import Splitter
from Products.GenericSetup.browser.manage import ExportStepsView
from Products.GenericSetup.browser.manage import ImportStepsView
from Products.StandardCacheManagers.AcceleratedHTTPCacheManager import (
    AcceleratedHTTPCacheManager
)
from Products.StandardCacheManagers.RAMCacheManager import RAMCacheManager
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import clearSite
from zope.component.hooks import setSite
from zope.interface.interfaces import IComponentLookup
from zope.interface.interfaces import IComponentRegistry
from zope.location.interfaces import ISite


class TestPortalCreation(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.workflow = self.portal.portal_workflow
        self.types = self.portal.portal_types
        self.cp = self.portal.portal_controlpanel
        self.actions = self.portal.portal_actions
        self.properties = self.portal.portal_properties
        self.memberdata = self.portal.portal_memberdata
        self.catalog = self.portal.portal_catalog
        self.groups = self.portal.portal_groups
        self.skins = self.portal.portal_skins
        self.transforms = self.portal.portal_transforms
        self.setup = self.portal.portal_setup

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
        self.assertTrue(hasattr(self.folder, 'logo.png'))

    def testNoIndexHtmlDocument(self):
        # The portal should not contain an index_html Document
        self.assertFalse('index_html' in self.portal)

    def testCanViewManagementScreen(self):
        # Make sure the ZMI management screen works
        self.setRoles(['Manager'])
        self.portal.manage_main()

    def testWorkflowIsActionProvider(self):
        # The workflow tool is one of the last remaining action providers.
        self.assertTrue(
            'portal_workflow' in self.actions.listActionProviders()
        )

    def testPortalIsIndexed(self):
        # The Plone site should be cataloged
        res = self.catalog(getId="plone")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, "plone")
        self.assertEqual(res[0].Title, "Welcome to Plone")

    def testMembersFolderMetaType(self):
        # Members folder should have meta_type 'Dexterity Container'
        members = self.membership.getMembersFolder()
        self.assertEqual(members.meta_type, 'Dexterity Container')

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

    def testMembersFolderDefaultView(self):
        members = self.membership.getMembersFolder()
        self.assertEqual(members.layout, '@@member-search')

    def testMailHost(self):
        # MailHost should be of the standard variety
        mailhost = self.portal.MailHost
        self.assertEqual(mailhost.meta_type, 'Mail Host')

    def testFolderEditActionHasEditTitle(self):
        # Edit tab of folders should be named 'edit', not 'properties'
        folder = self.types.getTypeInfo('Folder')
        for action in folder._cloneActions():
            if action.id == 'edit':
                self.assertEqual(action.title, 'Edit')
                break
        else:
            self.fail("Folder has no 'edit' action")

    def testNoPortalFormTool(self):
        # portal_form should have been removed
        self.assertFalse('portal_form' in self.portal)

    def testNoPortalNavigationTool(self):
        # portal_navigation should have been removed
        self.assertFalse('portal_navigation' in self.portal)

    def testNoFormProperties(self):
        # form_properties should have been removed
        self.assertFalse('form_properties' in self.properties)

    def testNoNavigationProperties(self):
        # navigation_properties should have been removed
        self.assertFalse('navigation_properties' in self.properties)

    def testFormToolTipsProperty(self):
        # formtooltips should have been removed
        self.assertFalse(self.memberdata.hasProperty('formtooltips'))

    def testNavTreeProperties(self):
        # navtree_properties should contain the new properties
        self.assertFalse(
            self.properties.navtree_properties.hasProperty(
                'parentMetaTypesNotToQuery'
            )
        )
        self.assertFalse(
            self.properties.navtree_properties.hasProperty('sitemapDepth')
        )
        self.assertFalse(
            self.properties.navtree_properties.hasProperty('showAllParents')
        )
        self.assertFalse(
            self.properties.navtree_properties.hasProperty(
                'metaTypesNotToList'
            )
        )  # noqa
        self.assertFalse(
            self.properties.navtree_properties.hasProperty('sortAttribute')
        )
        self.assertFalse(
            self.properties.navtree_properties.hasProperty('sortOrder')
        )

        registry = getUtility(IRegistry)
        self.assertTrue('plone.workflow_states_to_show' in registry)
        self.assertTrue('plone.filter_on_workflow' in registry)
        self.assertTrue('plone.sitemap_depth' in registry)
        self.assertTrue('plone.root' in registry)
        self.assertTrue('plone.sort_tabs_on' in registry)
        self.assertTrue('plone.sort_tabs_reversed' in registry)
        self.assertTrue('plone.displayed_types' in registry)
        self.assertTrue('plone.parent_types_not_to_query' in registry)

    def testSitemapAction(self):
        # There should be a sitemap action
        for action in self.actions.listActions():
            if action.getId() == 'sitemap':
                break
        else:
            self.fail("Actions tool has no 'sitemap' action")

    def testUnfriendlyTypesProperty(self):
        # We should have an types_not_searched property
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSchema, prefix="plone")
        self.assertTrue('plone.types_not_searched' in registry)
        self.assertTrue('Plone Site' in settings.types_not_searched)

    def testDefaultSortOrderProperty(self):
        # We should have an sort_on property
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSchema, prefix="plone")
        self.assertIn('plone.sort_on', registry)
        self.assertEqual(settings.sort_on, 'relevance')

    def testNonDefaultPageTypes(self):
        # We should have a default_page_types setting
        registry = self.portal.portal_registry
        self.assertIn('plone.default_page_types', registry)
        self.assertNotIn('Folder', registry['plone.default_page_types'])
        self.assertIn('Document', registry['plone.default_page_types'])

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
        res = self.catalog(
            path={'query': '/plone/news/aggregator', 'depth': 0}
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'aggregator')
        self.assertEqual(res[0].Title, 'News')
        self.assertEqual(res[0].Description, 'Site News')

    def testEventsTopicIsIndexed(self):
        # Events (smart) folder should be cataloged
        res = self.catalog(
            path={'query': '/plone/events/aggregator', 'depth': 0}
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'aggregator')
        self.assertEqual(res[0].Title, 'Events')
        self.assertEqual(res[0].Description, 'Site Events')

    def testNewsFolderIsIndexed(self):
        # News folder should be cataloged
        res = self.catalog(path={'query': '/plone/news', 'depth': 0})
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'news')
        self.assertEqual(res[0].Title, 'News')
        self.assertEqual(res[0].Description, 'Site News')

    def testEventsFolderIsIndexed(self):
        # Events folder should be cataloged
        res = self.catalog(path={'query': '/plone/events', 'depth': 0})
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].getId, 'events')
        self.assertEqual(res[0].Title, 'Events')
        self.assertEqual(res[0].Description, 'Site Events')

    def testNewsFolder(self):
        self.assertTrue('news' in self.portal.objectIds())
        folder = getattr(self.portal, 'news')
        self.assertEqual(folder.portal_type, 'Folder')
        self.assertEqual(folder._ordering, 'unordered')
        self.assertEqual(folder.getDefaultPage(), 'aggregator')
        self.assertEqual(folder.immediately_addable_types, ['News Item'])

    def testEventsFolder(self):
        self.assertTrue('events' in self.portal.objectIds())
        folder = getattr(self.portal, 'events')
        self.assertEqual(folder.portal_type, 'Folder')
        self.assertEqual(folder._ordering, 'unordered')
        self.assertEqual(folder.getDefaultPage(), 'aggregator')
        self.assertEqual(folder.immediately_addable_types, ['Event'])

    def testNewsCollection(self):
        # News collection is in place as default view and has a criterion to
        # show only News Items, and uses the folder_summary_view.
        self.assertEqual(
            ['aggregator'], [i for i in self.portal.news.objectIds()]
        )
        collection = getattr(self.portal.news, 'aggregator')
        self.assertEqual(collection._getPortalTypeName(), 'Collection')
        query = collection.query
        self.assertTrue(
            {
                'i': 'portal_type',
                'o': 'plone.app.querystring.operation.selection.any',
                'v': ['News Item'],
            }
            in query
        )
        self.assertTrue(
            {
                'i': 'review_state',
                'o': 'plone.app.querystring.operation.selection.any',
                'v': ['published'],
            }
            in query
        )
        self.assertEqual(collection.getLayout(), 'summary_view')

    def testEventsCollection(self):
        # Events collection is in place as default view and has criterion to
        # show only future Events Items.
        self.assertEqual(
            ['aggregator'], [i for i in self.portal.events.objectIds()]
        )
        collection = getattr(self.portal.events, 'aggregator')
        self.assertEqual(collection._getPortalTypeName(), 'Collection')
        query = collection.query
        self.assertTrue(
            {
                'i': 'portal_type',
                'o': 'plone.app.querystring.operation.selection.any',
                'v': ['Event'],
            }
            in query
        )
        self.assertTrue(
            {
                'i': 'review_state',
                'o': 'plone.app.querystring.operation.selection.any',
                'v': ['published'],
            }
            in query
        )
        self.assertEqual(collection.getLayout(), 'event_listing')

    def testObjectButtonActions(self):
        self.setRoles(['Manager', 'Member'])
        atool = self.actions
        self.assertFalse(atool.getActionInfo('object_buttons/cut') is None)
        self.assertFalse(atool.getActionInfo('object_buttons/copy') is None)
        self.assertFalse(atool.getActionInfo('object_buttons/paste') is None)
        self.assertFalse(atool.getActionInfo('object_buttons/delete') is None)

    def testContentsTabVisible(self):
        for a in self.actions.listActions():
            if a.getId() == 'folderContents':
                self.assertTrue(a.visible)

    def testDefaultGroupsAdded(self):
        self.assertTrue('Administrators' in self.groups.listGroupIds())
        self.assertTrue('Reviewers' in self.groups.listGroupIds())

    def testGenerateTabsSiteProperty(self):
        # The generate_tabs site property should be emtpy
        registry = getUtility(IRegistry)
        navigation_settings = registry.forInterface(
            INavigationSchema, prefix="plone"
        )
        self.assertTrue('plone.generate_tabs' in registry)
        self.assertTrue(navigation_settings.generate_tabs)

    def testSelectableViewsOnFolder(self):
        views = self.portal.portal_types.Folder.getAvailableViewMethods(None)
        self.assertTrue('listing_view' in views)
        self.assertTrue('album_view' in views)

    def testSelectableViewsOnTopic(self):
        views = self.portal.portal_types.Collection.getAvailableViewMethods(
            None
        )
        self.assertTrue('listing_view' in views)
        self.assertTrue('album_view' in views)

    def testLocationMemberdataProperty(self):
        # portal_memberdata should have a location property
        self.assertTrue(self.memberdata.hasProperty('location'))

    def testLanguageMemberdataProperty(self):
        # portal_memberdata should have a language property
        self.assertTrue(self.memberdata.hasProperty('language'))

    def testDescriptionMemberdataProperty(self):
        # portal_memberdata should have a description property
        self.assertTrue(self.memberdata.hasProperty('description'))

    def testHome_PageMemberdataProperty(self):
        # portal_memberdata should have a home_page property
        self.assertTrue(self.memberdata.hasProperty('home_page'))

    def testExtEditorMemberdataProperty(self):
        # portal_memberdata should have a location property
        self.assertEqual(self.memberdata.getProperty('ext_editor'), 0)

    def testSiteSetupActionIsPresent(self):
        actions = self.actions.listActions()
        self.assertEqual(
            [x.title for x in actions if x.title == 'Site Setup'],
            ['Site Setup'],
        )

    def testEnableLivesearchProperty(self):
        # registry should have enable_livesearch property
        registry = getUtility(IRegistry)
        self.assertTrue('plone.enable_livesearch' in registry)

    def testRedirectLinksProperty(self):
        registry = getUtility(IRegistry)
        self.assertTrue('plone.redirect_links' in registry)
        self.assertEqual(True, registry['plone.redirect_links'])

    def testLinkDefaultView(self):
        self.assertEqual(self.types.Link.default_view, 'link_redirect_view')

    def testTTWLockableProperty(self):
        registry = getUtility(IRegistry)
        self.assertTrue('plone.lock_on_ttw_edit' in registry)
        self.assertEqual(True, registry['plone.lock_on_ttw_edit'])

    def testPortalFTIIsDynamicFTI(self):
        # Plone Site FTI should be a Dexterity FTI
        fti = self.portal.getTypeInfo()
        self.assertEqual(fti.meta_type, 'Dexterity FTI')

    def testPloneSiteFTIHasMethodAliases(self):
        # Should add method aliases to the Plone Site FTI
        expected_aliases = {
            '(Default)': '(dynamic view)',
            'view': '(selected layout)',
            'edit': '@@edit',
            'sharing': '@@sharing',
        }
        fti = self.portal.getTypeInfo()
        aliases = fti.getMethodAliases()
        self.assertEqual(aliases, expected_aliases)

    def testSiteActions(self):
        self.setRoles(['Manager', 'Member'])
        atool = self.actions
        self.assertFalse(atool.getActionInfo('site_actions/sitemap') is None)
        self.assertFalse(atool.getActionInfo('site_actions/contact') is None)
        self.assertFalse(
            atool.getActionInfo('site_actions/accessibility') is None
        )

    def testSetupAction(self):
        self.setRoles(['Manager', 'Member'])
        atool = self.actions
        self.assertFalse(atool.getActionInfo('user/plone_setup') is None)

    def testTypesHaveSelectedLayoutViewAction(self):
        # Should add method aliases to the Plone Site FTI
        types = (
            'Document',
            'Event',
            'File',
            'Folder',
            'Image',
            'Link',
            'News Item',
            'Collection',
            'Plone Site',
        )
        for typeName in types:
            fti = getattr(self.types, typeName)
            aliases = fti.getMethodAliases()
            self.assertEqual(aliases['view'], '(selected layout)')

    def testPortalUsesMethodAliases(self):
        fti = self.portal.getTypeInfo()
        for action in fti.listActions():
            if action.getId() == 'edit':
                self.assertEqual(
                    action.getActionExpression(), 'string:${object_url}/edit'
                )
            if action.getId() == 'sharing':
                self.assertEqual(
                    action.getActionExpression(),
                    'string:${object_url}/sharing',
                )

    def testNavigationAndSearchPanelsInstalled(self):
        # Navigation and search panels should be installed
        haveSearch = False
        haveNavigation = False
        for panel in self.cp.listActions():
            if panel.getId() == 'SearchSettings':
                haveSearch = True
            elif panel.getId() == 'NavigationSettings':
                haveNavigation = True
        self.assertTrue(haveSearch and haveNavigation)

    def testOwnerHasAccessInactivePermission(self):
        permission_on_role = [
            p
            for p in self.portal.permissionsOfRole('Owner')
            if p['name'] == AccessInactivePortalContent
        ][0]
        self.assertTrue(permission_on_role['selected'])
        cur_perms = self.portal.permission_settings(
            AccessInactivePortalContent
        )[0]
        self.assertTrue(cur_perms['acquire'])

    def testSyndicationEnabledByDefault(self):
        syn = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="syndication-util"
        )
        self.assertTrue(syn.site_enabled())

    # FIXME: Syndication is not enabled by default in DX
    def testSyndicationEnabledOnNewsAndEvents(self):
        syn = getMultiAdapter(
            (self.portal.news.aggregator, self.portal.REQUEST),
            name="syndication-util",
        )
        self.assertFalse(syn.context_enabled())
        syn = getMultiAdapter(
            (self.portal.events.aggregator, self.portal.REQUEST),
            name="syndication-util",
        )
        self.assertFalse(syn.context_enabled())

    def testSyndicationTabDisabled(self):
        # Syndication tab should be disabled by default
        for action in self.actions.listActions():
            if action.getId() == 'syndication' and action.visible:
                self.fail(
                    "Actions tool still has visible 'syndication' action"
                )

    def testObjectButtonActionsInvisibleOnPortalDefaultDocument(self):
        # only a manager would have proper permissions
        self.setRoles(['Manager', 'Member'])
        self.portal.invokeFactory('Document', 'index_html')
        acts = self.actions.listFilteredActionsFor(self.portal.index_html)
        buttons = acts.get('object_buttons', [])
        self.assertEqual(0, len(buttons))

    def testObjectButtonActionsOnDefaultDocumentDoNotApplyToParent(self):
        # only a manager would have proper permissions
        self.setRoles(['Manager', 'Member'])
        self.folder.invokeFactory('Document', 'index_html')
        acts = self.actions.listFilteredActionsFor(self.folder.index_html)
        buttons = acts['object_buttons']
        self.assertEqual(len(buttons), 5)
        urls = [a['url'] for a in buttons]
        for url in urls:
            self.assertFalse(
                'index_html' not in url,
                'Action wrongly applied to parent object %s' % url,
            )  # noqa

    def testObjectButtonActionsPerformCorrectAction(self):
        # only a manager would have proper permissions
        self.setRoles(['Manager', 'Member'])
        self.folder.invokeFactory('Document', 'index_html')
        acts = self.actions.listFilteredActionsFor(self.folder.index_html)
        buttons = acts['object_buttons']
        self.assertEqual(len(buttons), 5)
        # special case for delete which needs a confirmation form,
        # and for redirection which does not confirm to the url policy,
        # which apparently is that action id X should have url object_X.
        urls = [
            (a['id'], a['url']) for a in buttons if a['id'] not in
            ('delete', 'redirection')
        ]
        for url in urls:
            # ensure that e.g. the 'copy' url contains object_copy
            self.assertTrue(
                'object_' + url[0] in url[1],
                "%s does not perform the expected object_%s action"
                % (url[0], url[0]),
            )

        delete_action = [
            (a['id'], a['url']) for a in buttons if a['id'] == 'delete'
        ][0]
        self.assertTrue(
            'delete_confirmation' in delete_action[1],
            "object_delete does not use the confirmation form",
        )

        redirection_action = [
            (a['id'], a['url']) for a in buttons if a['id'] == 'redirection'
        ][0]
        self.assertIn('@@manage-aliases', redirection_action[1])

    def testObjectButtonActionsInExpectedOrder(self):
        # The object buttons need to be in a standardized order
        self.setRoles(['Manager', 'Member'])
        # fill the copy buffer so we see all actions
        self.folder.cb_dataValid = True
        acts = self.actions.listFilteredActionsFor(self.folder)
        buttons = acts['object_buttons']
        self.assertEqual(len(buttons), 7)
        ids = [(a['id']) for a in buttons]
        self.assertEqual(
            ids,
            ['cut', 'copy', 'paste', 'delete', 'rename',
             'redirection',
             'ical_import_enable',
             ],
        )

    def testCustomSkinFolderExists(self):
        # the custom skin needs to be created
        self.assertTrue('custom' in self.skins)

    def testCustomSkinFolderComesFirst(self):
        firstInDefaultSkin = self.skins.getSkinPath('Plone Default').split(
            ','
        )[0]
        self.assertEqual(
            firstInDefaultSkin,
            'custom',
            "The 'custom' layer was not the first in the Plone Default skin. "
            "It was %r." % firstInDefaultSkin,
        )

    def testMemberHasViewGroupsPermission(self):
        # Member should be granted the 'View Groups' permission
        member_has_permission = [
            p
            for p in self.portal.permissionsOfRole('Member')
            if p['name'] == 'View Groups'
        ][0]
        self.assertTrue(member_has_permission['selected'])

    def testDiscussionItemWorkflow(self):
        # By default the discussion item has the comment_one_state_workflow
        self.assertEqual(
            self.workflow.getChainForPortalType('Discussion Item'),
            ('comment_one_state_workflow',),
        )

    def testFolderHasFolderListingView(self):
        # Folder type should allow 'folder_listing'
        self.assertTrue('listing_view' in self.types.Folder.view_methods)

    def testFolderHasSummaryView(self):
        # Folder type should allow 'folder_summary_view'
        self.assertTrue('summary_view' in self.types.Folder.view_methods)

    def testFolderHasTabularView(self):
        # Folder type should allow 'folder_tabular_view'
        self.assertTrue('tabular_view' in self.types.Folder.view_methods)

    def testFolderHasAlbumView(self):
        # Folder type should allow 'atct_album_view'
        self.assertTrue('album_view' in self.types.Folder.view_methods)

    def testConfigurableSafeHtmlTransform(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IFilterSchema, prefix="plone")
        # The safe_html transformation should be configurable
        try:
            settings.disable_filtering
        except (AttributeError, KeyError):
            self.fail('Disabling of safe_html should be possible!')

    def testCacheManagers(self):
        # The cache and caching policy managers should exist
        httpcache = self.portal._getOb('HTTPCache', None)
        ramcache = self.portal._getOb('RAMCache', None)
        cpm = self.portal._getOb('caching_policy_manager', None)
        self.assertTrue(isinstance(httpcache, AcceleratedHTTPCacheManager))
        self.assertTrue(isinstance(ramcache, RAMCacheManager))
        self.assertTrue(isinstance(cpm, CachingPolicyManager))

    def testHomeActionUsesView(self):
        actions = self.actions.listActions()
        homeAction = [x for x in actions if x.id == 'index_html'][0]
        self.assertEqual(
            homeAction.getInfoData()[0]['url'].text,
            'string:${globals_view/navigationRootUrl}',
        )

    def testPloneLexicon(self):
        # Plone lexicon should use new splitter and case normalizer
        pipeline = self.catalog.plone_lexicon._pipeline
        self.assertTrue(len(pipeline) >= 2)
        self.assertTrue(isinstance(pipeline[0], Splitter))
        self.assertTrue(isinstance(pipeline[1], I18NNormalizer))

    def testMakeSnapshot(self):
        # GenericSetup snapshot should work
        self.setRoles(['Manager'])
        snapshot_id = self.setup._mangleTimestampName('test')
        self.setup.createSnapshot(snapshot_id)

    def testSiteManagerSetup(self):
        clearSite()
        # The portal should be an ISite
        self.assertTrue(ISite.providedBy(self.portal))
        # There should be a IComponentRegistry
        comp = IComponentLookup(self.portal)
        IComponentRegistry.providedBy(comp)

        # Test if we get the right site managers
        gsm = getGlobalSiteManager()
        sm = getSiteManager()
        # Without setting the site we should get the global site manager
        self.assertTrue(sm is gsm)

        # Now we set the site, as it is done in url traversal normally
        setSite(self.portal)
        # And should get the local site manager
        sm = getSiteManager()
        self.assertTrue(aq_base(sm) is aq_base(comp))

    def testUtilityRegistration(self):
        gsm = getGlobalSiteManager()
        # Work around five.localsitemanger assuming the global site manager
        # has no bases, which is not true in the test layer.
        old_bases = gsm.__bases__
        gsm.__bases__ = ()

        try:
            global_util = dummy.DummyUtility()

            # Register a global utility and see if we can get it
            gsm.registerUtility(global_util, dummy.IDummyUtility)
            getutil = getUtility(dummy.IDummyUtility)
            self.assertEqual(getutil, global_util)

            # Register a local utility and see if we can get it
            sm = getSiteManager()
            local_util = dummy.DummyUtility()

            sm.registerUtility(local_util, dummy.IDummyUtility)
            getutil = getUtility(dummy.IDummyUtility)
            self.assertEqual(getutil, local_util)
            # Clean up the site again
            clearSite()

            # Without a site we get the global utility
            getutil = getUtility(dummy.IDummyUtility)
            self.assertEqual(getutil, global_util)

            # Clean up again and unregister the utilites
            gsm.unregisterUtility(provided=dummy.IDummyUtility)
            sm.unregisterUtility(provided=dummy.IDummyUtility)

            # Make sure unregistration was successful
            util = queryUtility(dummy.IDummyUtility)
            self.assertTrue(util is None)
        finally:
            gsm.__bases__ = old_bases

    def testPortletManagersInstalled(self):
        sm = getSiteManager(self.portal)
        registrations = [
            r.name
            for r in sm.registeredUtilities()
            if IPortletManager == r.provided
        ]
        self.assertEqual(
            [
                'plone.dashboard1',
                'plone.dashboard2',
                'plone.dashboard3',
                'plone.dashboard4',
                'plone.footerportlets',
                'plone.leftcolumn',
                'plone.rightcolumn',
            ],
            sorted(registrations),
        )

    def testPortletAssignmentsAtRoot(self):
        leftColumn = getUtility(IPortletManager, name='plone.leftcolumn')
        rightColumn = getUtility(IPortletManager, name='plone.rightcolumn')

        left = getMultiAdapter(
            (self.portal, leftColumn), IPortletAssignmentMapping
        )
        right = getMultiAdapter(
            (self.portal, rightColumn), IPortletAssignmentMapping
        )

        self.assertEqual(len(left), 1)
        self.assertEqual(len(right), 2)

    def testPortletBlockingForMembersFolder(self):
        members = self.portal.Members
        rightColumn = getUtility(IPortletManager, name='plone.rightcolumn')
        portletAssignments = getMultiAdapter(
            (members, rightColumn), ILocalPortletAssignmentManager
        )
        self.assertEqual(
            True, portletAssignments.getBlacklistStatus(CONTEXT_PORTLETS)
        )

    def testAddablePortletsInColumns(self):
        for name in ('plone.leftcolumn', 'plone.rightcolumn'):
            column = getUtility(IPortletManager, name=name)
            addable_types = [
                p.addview for p in column.getAddablePortletTypes()
            ]
            addable_types.sort()
            self.assertEqual(
                [
                    'plone.portlet.collection.Collection',
                    'plone.portlet.static.Static',
                    'portlets.Actions',
                    'portlets.Calendar',
                    'portlets.Classic',
                    'portlets.Events',
                    'portlets.Login',
                    'portlets.Navigation',
                    'portlets.News',
                    'portlets.Recent',
                    'portlets.Review',
                    'portlets.Search',
                    'portlets.rss',
                ],
                addable_types,
            )

    def testAddablePortletsInDashboard(self):
        for name in (
            'plone.dashboard1',
            'plone.dashboard2',
            'plone.dashboard3',
            'plone.dashboard4',
        ):
            column = getUtility(IPortletManager, name=name)
            addable_types = [
                p.addview for p in column.getAddablePortletTypes()
            ]
            addable_types.sort()
            self.assertEqual(
                [
                    'plone.portlet.collection.Collection',
                    'plone.portlet.static.Static',
                    'portlets.Actions',
                    'portlets.Calendar',
                    'portlets.Classic',
                    'portlets.Events',
                    'portlets.News',
                    'portlets.Recent',
                    'portlets.Review',
                    'portlets.Search',
                    'portlets.rss',
                ],
                addable_types,
            )

    def testReaderEditorRoles(self):
        self.assertTrue('Reader' in self.portal.valid_roles())
        self.assertTrue('Editor' in self.portal.valid_roles())
        self.assertTrue(
            'Reader' in self.portal.acl_users.portal_role_manager.listRoleIds()
        )
        self.assertTrue(
            'Editor' in self.portal.acl_users.portal_role_manager.listRoleIds()
        )
        self.assertTrue(
            'View'
            in [
                r['name']
                for r in self.portal.permissionsOfRole('Reader')
                if r['selected']
            ]
        )
        self.assertTrue(
            'Modify portal content'
            in [
                r['name']
                for r in self.portal.permissionsOfRole('Editor')
                if r['selected']
            ]
        )

    def testWorkflowsInstalled(self):
        for wf in [
            'intranet_workflow',
            'intranet_folder_workflow',
            'one_state_workflow',
            'simple_publication_workflow',
        ]:
            self.assertTrue(wf in self.portal.portal_workflow)

    def testAddPermisssionsGivenToContributorRole(self):
        self.assertTrue('Contributor' in self.portal.valid_roles())
        self.assertTrue(
            'Contributor'
            in self.portal.acl_users.portal_role_manager.listRoleIds()
        )
        for p in [
            'Add portal content',
            'Add portal folders',
            'plone.app.contenttypes: Add Document',
            'plone.app.contenttypes: Add Event',
            'plone.app.contenttypes: Add File',
            'plone.app.contenttypes: Add Folder',
            'plone.app.contenttypes: Add Link',
            'plone.app.contenttypes: Add News Item',
        ]:
            self.assertTrue(
                p
                in [
                    r['name']
                    for r in self.portal.permissionsOfRole('Contributor')
                    if r['selected']
                ]
            )

    def testSharingAction(self):
        # Should be in portal_actions
        self.assertTrue('local_roles' in self.actions.object)

        # Should not be in any of the default FTIs
        for fti in self.types.values():
            self.assertFalse(
                'local_roles' in [a.id for a in fti.listActions()]
            )

    def testSecondaryEditorPermissionsGivenToEditorRole(self):
        for p in [
            'Manage properties',
            'Modify view template',
            'Request review',
        ]:
            self.assertTrue(
                p
                in [
                    r['name']
                    for r in self.portal.permissionsOfRole('Editor')
                    if r['selected']
                ]
            )

    def testNonFolderishTabsProperty(self):
        registry = getUtility(IRegistry)
        navigation_settings = registry.forInterface(
            INavigationSchema, prefix="plone"
        )
        self.assertEqual(True, navigation_settings.nonfolderish_tabs)

    def testNoDoubleGenericSetupImportSteps(self):
        view = ImportStepsView(self.setup, None)
        self.assertEqual([i['id'] for i in view.doubleSteps()], [])

    def testNoInvalidGenericSetupImportSteps(self):
        view = ImportStepsView(self.setup, None)
        self.assertEqual([i['id'] for i in view.invalidSteps()], [])

    def testNoDoubleGenericSetupExportSteps(self):
        view = ExportStepsView(self.setup, None)
        self.assertEqual([i['id'] for i in view.doubleSteps()], [])

    def testNoInvalidGenericSetupExportSteps(self):
        view = ExportStepsView(self.setup, None)
        self.assertEqual([i['id'] for i in view.invalidSteps()], [])


class TestPortalBugs(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.catalog = self.portal.portal_catalog
        self.setupAuthenticator()

    def testSubsequentProfileImportSucceeds(self):
        # Subsequent profile imports fail (#5439)
        self.loginAsPortalOwner()
        setup_tool = getToolByName(self.portal, "portal_setup")
        # this will raise an error if it fails
        profile = setup_tool.getBaselineContextID()
        setup_tool.runAllImportStepsFromProfile(profile, purge_old=True)
        self.assertTrue(1 == 1)

    def testFinalStepsWithMembersFolderDeleted(self):
        # We want the final steps to work even if the 'Members' folder
        # is gone
        self.loginAsPortalOwner()
        portal = self.portal
        portal.manage_delObjects(['Members'])
        setup_tool = getToolByName(self.portal, 'portal_setup')
        setuphandlers.importFinalSteps(setup_tool)  # raises error if fail
        self.assertTrue(1 == 1)


class TestManagementPageCharset(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.properties = self.portal.portal_properties

    def testManagementPageCharset(self):
        manage_charset = getattr(self.portal, 'management_page_charset', None)
        self.assertTrue(manage_charset)
        self.assertEqual(manage_charset, 'utf-8')


class TestAddPloneSite(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.request = self.app.REQUEST

    def addsite(self):
        self.loginAsPortalOwner()
        # Set up a request for the plone-addsite view.
        form = self.request.form
        form['form.submitted'] = 1
        form['site_id'] = 'plonesite1'
        form['setup_content'] = 1
        self.request['_authenticator'] = createToken()
        addsite = self.app.restrictedTraverse('@@plone-addsite')
        addsite()

    def test_addsite_en_as_nl(self):
        # Add an English site with a Dutch browser.
        self.request['HTTP_ACCEPT_LANGUAGE'] = 'nl'
        self.request.form['default_language'] = 'en'
        self.addsite()
        plonesite = self.app.plonesite1
        # Unfortunately, the next test passes even without the fix (overriding
        # HTTP_ACCEPT_LANGUAGE on the request in factory.py).  This seems to be
        # because translations are not available in the tests.
        self.assertIn('Learn more about Plone', plonesite.text.raw)

        # XXX maybe it is better to reset the sire in the @@plone-addsite view
        # or somewhere else?
        setSite(None)
