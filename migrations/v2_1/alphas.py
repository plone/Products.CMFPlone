import os

from Acquisition import aq_base
from zExceptions import BadRequest
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct, \
     safeGetMemberDataTool
from Products.CMFCore.Expression import Expression
from Products.CMFPlone import transaction


def two05_alpha1(portal):
    """2.0.5 -> 2.1-alpha1
    """
    out = []

    # We do this earlier to avoid reindexing twice
    migrated = migrateCatalogIndexes(portal, out)
    reindex = tweakIndexes(portal, out)

    # Tweak Properties And CSS. This needs to happen earlier so that
    # ATCT migration doesn't fail
    tweakPropertiesAndCSS(portal, out)


    if not migrated and reindex:
        refreshSkinData(portal, out)
        reindexCatalog(portal, out)
    
    # FIXME: Must get rid of this!
    # ATCT is not installed when SUPPRESS_ATCT_INSTALLATION is set to YES
    # It's required for some unit tests in ATCT [tiran]
    suppress_atct = bool(os.environ.get('SUPPRESS_ATCT_INSTALLATION', None)
                         == 'YES')

    # Install SecureMailHost
    replaceMailHost(portal, out)

    # Remove legacy tools
    deleteTool(portal, out, 'portal_form')
    deleteTool(portal, out, 'portal_navigation')

    # Remove old properties
    deletePropertySheet(portal, out, 'form_properties')
    deletePropertySheet(portal, out, 'navigation_properties')

    # Install Archetypes
    installArchetypes(portal, out)

    # Install ATContentTypes
    if not suppress_atct:
        installATContentTypes(portal, out)

        # Switch over to ATCT
        #migrateToATCT(portal, out)
        migrateToATCT10(portal, out)

    transaction.commit(1)
    
    return out

def tweakPropertiesAndCSS(portal, out):
    # Install CSS and Javascript registries
    # also install default CSS and JS in the registry tools
    installCSSandJSRegistries(portal, out)
    
    # Add translation service tool to portal root
    addTranslationServiceTool(portal, out)

    # Add new memberdata properties
    addMemberdataHome_Page(portal, out)
    addMemberdataLocation(portal, out)
    addMemberdataDescription(portal, out)
    addMemberdataLanguage(portal, out)
    addMemberdataExtEditor(portal,out)

    # Update navtree_properties
    updateNavTreeProperties(portal, out)

def tweakIndexes(portal, out):
    reindex = 0

    # Switch path index to ExtendedPathIndex
    reindex += switchPathIndex(portal, out)

    # Add getObjPositionInParent index
    reindex += addGetObjPositionInParentIndex(portal, out)

    # Add getObjSize support to catalog
    reindex += addGetObjSizeMetadata(portal, out)

    # Add exclude_from_nav metadata
    reindex += addExclude_from_navMetadata(portal, out)

    # Install DateIndexes and DateRangeIndexes
    reindex += migrateDateIndexes(portal, out)
    reindex += migrateDateRangeIndexes(portal, out)

    # Add sortable_title index
    reindex += addSortable_TitleIndex(portal, out)

    # add is_folderish metadata
    reindex += addIs_FolderishMetadata(portal, out)

    # Get rid of CMF typo 'ExpiresDate' metadata in favor of proper DC
    # 'ExpirationDate' metadata
    reindex += switchToExpirationDateMetadata(portal, out) 

    return reindex

def alpha1_alpha2(portal):
    """2.1-alpha1 -> 2.1-alpha2
    """
    out = []

    reindex = 0

    # Add full_screen action
    addFullScreenAction(portal, out)
    addFullScreenActionIcon(portal, out)

    # Make visible_ids a site-wide property
    addVisibleIdsSiteProperty(portal, out)
    deleteVisibleIdsMemberProperty(portal, out)

    # Remove obsolete formtooltips property
    deleteFormToolTipsMemberProperty(portal, out)

    # Make a new property exposeDCMetaTags
    addExposeDCMetaTagsProperty(portal, out)

    # Add sitemap action
    addSitemapAction(portal, out)

    # Add types_not_searched site property
    addUnfriendlyTypesSiteProperty(portal, out)

    # Add non_default_page_types site property
    addNonDefaultPageTypesSiteProperty(portal, out)

    # Remove old portal_tabs actions
    removePortalTabsActions(portal, out)

    # Add news folder
    addNewsFolder(portal, out)

    # Add news topic
    addNewsTopic(portal, out)

    # Add events folder
    addEventsFolder(portal, out)

    # Add events topic
    addEventsTopic(portal, out)

    # Add objec cut/copy/paste/delete + batch buttons
    addEditContentActions(portal, out)

    # Add groups 'administrators' and 'reviewers'
    addDefaultGroups(portal, out)

    # Put default types in portal_factory
    addDefaultTypesToPortalFactory(portal, out)

    # Add non_default_page_types site property
    addDisableFolderSectionsSiteProperty(portal, out)

    # Add selectable_views to portal root
    addSiteRootViewTemplates(portal, out)

    # Fix the conditions and permissions on the folder_buttons actions
    fixFolderButtonsActions(portal, out)

    # Change the condition for the change_state action
    alterChangeStateActionCondition(portal, out)
    
    # Change condition for the external editor action so it checks for the
    # user preferences.
    alterExtEditorActionCondition(portal, out)

    # Add typesUseViewActionInListings site_property for types like Image and File,
    # which shouldn't use immediate_view from folder_contents and listings
    addTypesUseViewActionInListingsProperty(portal, out)

    # Change name of plone_setup action
    changePloneSetupActionToSiteSetup(portal,out)

    # Change plone site FTI icon
    changePloneSiteIcon(portal, out)
    
    # ADD NEW STUFF BEFORE THIS LINE AND LEAVE THE TRAILER ALONE!

    # Rebuild catalog
    if reindex:
        refreshSkinData(portal, out)
        reindexCatalog(portal, out)

    # FIXME: *Must* be called after reindexCatalog.
    # In tests, reindexing loses the folders for some reason...

    # Make sure the Members folder is cataloged
    indexMembersFolder(portal, out)

    # Make sure the News folder is cataloged
    indexNewsFolder(portal, out)

    # Make sure the Events folder is cataloged
    indexEventsFolder(portal, out)
    
    return out


def addTranslationServiceTool(portal, out):
    """Adds the TranslationServiceTool to portal."""
    addCMFPloneTool = portal.manage_addProduct['CMFPlone'].manage_addTool
    translationServiceTool = getToolByName(portal, 'translation_service', None)
    if translationServiceTool is None:
        addCMFPloneTool('Portal Translation Service Tool', None)
        out.append('Added TranslationService Tool')


def replaceMailHost(portal, out):
    """Replaces the mailhost with a secure mail host."""
    id = 'MailHost'
    oldmh = getattr(aq_base(portal), id)
    if oldmh.meta_type == 'Secure Mail Host':
        out.append('Secure Mail Host already installed')
        return
    title = oldmh.title
    smtp_host = oldmh.smtp_host
    smtp_port = oldmh.smtp_port
    portal.manage_delObjects([id])
    out.append('Removed old MailHost')

    addMailhost = portal.manage_addProduct['SecureMailHost'].manage_addMailHost
    addMailhost(id, title=title, smtp_host=smtp_host, smtp_port=smtp_port)
    out.append('Added new MailHost (SecureMailHost): %s:%s' % (smtp_host, smtp_port))


def deleteTool(portal, out, tool_name):
    """Deletes a tool."""
    if hasattr(aq_base(portal), tool_name):
        portal._delObject(tool_name)
    out.append('Deleted %s tool.' % tool_name)


def deletePropertySheet(portal, out, sheet_name):
    """Deletes a property sheet from portal_properties."""
    proptool = portal.portal_properties
    if hasattr(aq_base(proptool), sheet_name):
        proptool._delObject(sheet_name)
    out.append('Deleted %s property sheet.' % sheet_name)


def installArchetypes(portal, out):
    """Quickinstalls Archetypes if not installed yet."""
    for product_name in ('MimetypesRegistry', 'PortalTransforms', 'Archetypes'):
        installOrReinstallProduct(portal, product_name, out)


def installATContentTypes(portal, out):
    """Quickinstalls ATContentTypes if not installed yet."""
    for product_name in ('ATContentTypes',):
        installOrReinstallProduct(portal, product_name, out)


def migrateToATCT(portal, out):
    """Switches portal to ATContentTypes.
    """
    transaction.commit(1)
    migrateFromCMFtoATCT = portal.migrateFromCMFtoATCT
    switchCMF2ATCT = portal.switchCMF2ATCT
    #out.append('Migrating and switching to ATContentTypes ...')
    result = migrateFromCMFtoATCT()
    out.append(result)
    try:
        switchCMF2ATCT(skip_rename=False)
    except IndexError:
        switchCMF2ATCT(skip_rename=True)
    transaction.commit(1)
    #out.append('Switched portal to ATContentTypes.')


def migrateToATCT10(portal, out):
    """Switches portal to ATCT 1.0
    """
    transaction.commit(1)
    tool = portal.portal_atct
    tool.migrateToATCT()
    transaction.commit(1)


def addFullScreenAction(portal, out):
    """Adds the full screen mode action."""
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        for action in actionsTool.listActions():
            if action.getId() == 'full_screen':
                break # We already have the action
        else:
            actionsTool.addAction('full_screen',
                name='Toggle full screen mode',
                action='string:javascript:toggleFullScreenMode();',
                condition='member',
                permission=CMFCorePermissions.View,
                category='document_actions',
                visible=1,
                )
        out.append("Added 'full_screen' action to actions tool.")


def addFullScreenActionIcon(portal, out):
    """Adds an icon for the full screen mode action. """
    iconsTool = getToolByName(portal, 'portal_actionicons', None)
    if iconsTool is not None:
        for icon in iconsTool.listActionIcons():
            if icon.getActionId() == 'full_screen':
                break # We already have the icon
        else:
            iconsTool.addActionIcon(
                category='plone',
                action_id='full_screen',
                icon_expr='fullscreenexpand_icon.gif',
                title='Toggle full screen mode',
                )
        out.append("Added 'full_screen' icon to actionicons tool.")


def addVisibleIdsSiteProperty(portal, out):
    """Adds sitewide config for editable short names."""
    propTool = getToolByName(portal, 'portal_properties', None)
    if propTool is not None:
        propSheet = getattr(aq_base(propTool), 'site_properties', None)
        if propSheet is not None:
            if not propSheet.hasProperty('visible_ids'):
                propSheet.manage_addProperty('visible_ids', 0, 'boolean')
            out.append("Added 'visible_ids' property to site_properties.")


def deleteVisibleIdsMemberProperty(portal, out):
    """Deletes visible_ids memberdata property."""
    memberdata = safeGetMemberDataTool(portal)
    if memberdata is not None:
        if memberdata.hasProperty('visible_ids'):
            memberdata.manage_delProperties(['visible_ids'])
        out.append("Deleted 'visible_ids' property from portal_memberdata.")


def deleteFormToolTipsMemberProperty(portal, out):
    """Deletes formtooltips memberdata property."""
    memberdata = safeGetMemberDataTool(portal)
    if memberdata is not None:
        if memberdata.hasProperty('formtooltips'):
            memberdata.manage_delProperties(['formtooltips'])
        out.append("Deleted 'formtooltips' property from portal_memberdata.")


def addExposeDCMetaTagsProperty(portal, out):
    """Adds sitewide config for whether DC metatags are shown."""
    propTool = getToolByName(portal, 'portal_properties', None)
    if propTool is not None:
        propSheet = getattr(aq_base(propTool), 'site_properties', None)
        if propSheet is not None:
            if not propSheet.hasProperty('exposeDCMetaTags'):
                propSheet.manage_addProperty('exposeDCMetaTags', 0, 'boolean')
            out.append("Added 'exposeDCMetaTags' property to site_properties.")


def switchPathIndex(portal, out):
    """Changes the 'path' index to ExtendedPathIndex."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        try:
            index = catalog._catalog.getIndex('path')
        except KeyError:
            pass
        else:
            indextype = index.__class__.__name__
            if indextype == 'ExtendedPathIndex':
                return 0
            catalog.delIndex('path')
            out.append("Deleted %s 'path' from portal_catalog." % indextype)

        catalog.addIndex('path', 'ExtendedPathIndex')
        out.append("Added ExtendedPathIndex 'path' to portal_catalog.")
        return 1 # Ask for reindexing
    return 0


def addGetObjPositionInParentIndex(portal, out):
    """Adds the getObjPositionInParent FieldIndex."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        try:
            index = catalog._catalog.getIndex('getObjPositionInParent')
        except KeyError:
            pass
        else:
            indextype = index.__class__.__name__
            if indextype == 'FieldIndex':
                return 0
            catalog.delIndex('getObjPositionInParent')
            out.append("Deleted %s 'getObjPositionInParent' from portal_catalog." % indextype)

        catalog.addIndex('getObjPositionInParent', 'FieldIndex')
        out.append("Added FieldIndex 'getObjPositionInParent' to portal_catalog.")
        return 1 # Ask for reindexing
    return 0


def addGetObjSizeMetadata(portal, out):
    """Adds getObjSize column to the catalog."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        if 'getObjSize' in catalog.schema():
            return 0
        catalog.addColumn('getObjSize')
        out.append("Added 'getObjSize' metadata to portal_catalog.")
        return 1 # Ask for reindexing
    return 0


def updateNavTreeProperties(portal, out):
    """Updates navtree_properties for new NavTree."""
    # Plone setup has changed because of the new NavTree implementation.
    # StatelessTreeNav had a createNavTreePropertySheet method which is now
    # in Portal.py (including the new properties).
    # If typesTolist is not there we're dealing with a real migration:
    propTool = getToolByName(portal, 'portal_properties', None)
    if propTool is not None:
        propSheet = getattr(aq_base(propTool), 'navtree_properties', None)
        if propSheet is not None:
            if not propSheet.hasProperty('typesToList'):
                propSheet._setProperty('typesToList', ['Folder', 'Large Plone Folder', 'Topic'], 'lines')
            if not propSheet.hasProperty('sortAttribute'):
                propSheet._setProperty('sortAttribute', 'getObjPositionInParent', 'string')
            if not propSheet.hasProperty('sortOrder'):
                propSheet._setProperty('sortOrder', 'asc', 'string')
            if not propSheet.hasProperty('sitemapDepth'):
                propSheet._setProperty('sitemapDepth', 3, 'int')
            if not propSheet.hasProperty('showAllParents'):
                propSheet._setProperty('showAllParents', 1, 'boolean')
            out.append('Updated navtree_properties.')


def addSitemapAction(portal, out):
    """Adds the sitemap action."""
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        for action in actionsTool.listActions():
            if action.getId() == 'sitemap':
                break # We already have the action
        else:
            actionsTool.addAction('sitemap',
                name='Site Map',
                action='string:$portal_url/sitemap',
                condition='',
                permission=CMFCorePermissions.View,
                category='site_actions',
                visible=1,
                )
        out.append("Added 'sitemap' action to actions tool.")


def addDefaultGroups(portal, out):
    "Adds default groups Administrators and Reviewers."""
    # See http://plone.org/collector/3522
    groups = (
        {'id': 'Administrators',
         'title': 'Administrators',
         'roles': ('Manager',), },
        {'id': 'Reviewers',
         'title': 'Reviewers',
         'roles': ('Reviewer',), },
        )
    groupsTool = getToolByName(portal, 'portal_groups', None)
    acl_users = getToolByName(portal, 'acl_users', None)
    has_gruf_userfolder = hasattr(acl_users, 'getGroupByName')
    if groupsTool is not None and has_gruf_userfolder:
        # Don't create workspaces
        flag = groupsTool.groupWorkspacesCreationFlag
        groupsTool.groupWorkspacesCreationFlag = False

        for group in groups:
            # Group already exists:
            if groupsTool.getGroupById(group['id']): continue

            groupsTool.addGroup(group['id'],
                                group['roles'],
                                title = group['title'])
            out.append("Added default group '%s'." % group['id'])

        groupsTool.groupWorkspacesCreationFlag = flag


def refreshSkinData(portal, out=None):
    """Refreshes skins to make new scripts available in the
    current transaction.
    """
    if hasattr(portal, '_v_skindata'):
        portal._v_skindata = None
    if hasattr(portal, 'setupCurrentSkin'):
        portal.setupCurrentSkin()


def reindexCatalog(portal, out):
    """Rebuilds the portal_catalog."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        # Reduce threshold for the reindex run
        old_threshold = catalog.threshold
        pg_threshold = getattr(catalog, 'pgthreshold', 0)
        catalog.pgthreshold = 300
        catalog.threshold = 2000
        catalog.refreshCatalog(clear=1)
        catalog.threshold = old_threshold
        catalog.pgthreshold = pg_threshold
        out.append("Reindexed portal_catalog.")


def installCSSandJSRegistries(portal, out):
    """Installs the CSS and JS registries."""
    qi = getToolByName(portal, 'portal_quickinstaller', None)
    if qi is not None:
        if qi.isProductInstalled('CSSRegistry'):
            qi.uninstallProduct('CSSRegistry')
        if not qi.isProductInstalled('ResourceRegistries'):
            qi.installProduct('ResourceRegistries', locked=0)

        cssreg = getToolByName(portal, 'portal_css', None)
        if cssreg is not None:
            cssreg.clearStylesheets()
            # add the bottom ones and the ones with special expressions first.
            # since registering a stylesheet adds it to the top of the stack
            cssreg.registerStylesheet('ploneRTL.css', expression="python:object.isRightToLeft(domain='plone')")
            cssreg.registerStylesheet('plonePresentation.css', media='presentation')
            cssreg.registerStylesheet('plonePrint.css', media='print')
            cssreg.registerStylesheet('ploneMobile.css', media='handheld')
            cssreg.registerStylesheet('ploneGenerated.css', media="screen")
            cssreg.registerStylesheet('ploneMember.css', expression='not: portal/portal_membership/isAnonymousUser')
            cssreg.registerStylesheet('ploneColumns.css', media="screen")
            cssreg.registerStylesheet('ploneAuthoring.css', media="screen")
            cssreg.registerStylesheet('plonePublic.css', media="screen")
            cssreg.registerStylesheet('ploneBase.css', media="screen")
            cssreg.registerStylesheet('ploneCustom.css')

        jsreg = getToolByName(portal, 'portal_javascripts', None)
        if jsreg is not None:
            jsreg.clearScripts()
            jsreg.registerScript('register_function.js')
            jsreg.registerScript('plone_javascript_variables.js')
            jsreg.registerScript('nodeutilities.js')
            jsreg.registerScript('cookie_functions.js')
            jsreg.registerScript('livesearch.js')
            jsreg.registerScript('fullscreenmode.js')
            jsreg.registerScript('select_all.js')
            jsreg.registerScript('plone_menu.js')
            jsreg.registerScript('mark_special_links.js')
            jsreg.registerScript('collapsiblesections.js')
            jsreg.registerScript('highlightsearchterms.js')
            jsreg.registerScript('first_input_focus.js')
            jsreg.registerScript('folder_contents_filter.js')
            jsreg.registerScript('folder_contents_hideAddItems.js')
            jsreg.registerScript('styleswitcher.js')
            jsreg.registerScript('table_sorter.js')
            jsreg.registerScript('calendar_formfield.js')
            jsreg.registerScript('calendarpopup.js')
            jsreg.registerScript('ie5fixes.js')
            jsreg.registerScript('formUnload.js')
            jsreg.registerScript('sarissa.js')
            jsreg.registerScript('plone_minwidth.js' , enabled=False)
            jsreg.registerScript('correctPREformatting.js', enabled=False)
            jsreg.registerScript('vcXMLRPC.js', enabled=False)


        out.append('Installed CSSRegistry and JSRegistry.')


def addUnfriendlyTypesSiteProperty(portal, out):
    """Adds types_not_searched site property."""
    # Types which will be installed as "unfriendly" and thus hidden for search
    # purposes
    BASE_TYPES_NOT_SEARCHED = ['ATBooleanCriterion',
                             'ATDateCriteria',
                             'ATDateRangeCriterion',
                             'ATListCriterion',
                             'ATPortalTypeCriterion',
                             'ATReferenceCriterion',
                             'ATSelectionCriterion',
                             'ATSimpleIntCriterion',
                             'ATSimpleStringCriterion',
                             'ATSortCriterion',
                             'Discussion Item',
                             'Plone Site',
                             'TempFolder']

    propTool = getToolByName(portal, 'portal_properties', None)
    if propTool is not None:
        propSheet = getattr(propTool, 'site_properties', None)
        if propSheet is not None:
            if not propSheet.hasProperty('types_not_searched'):
                propSheet.manage_addProperty('types_not_searched',
                                             BASE_TYPES_NOT_SEARCHED,
                                             'lines')
            out.append("Added 'types_not_searched' property to site_properties.")


def addNonDefaultPageTypesSiteProperty(portal, out):
    """Adds non_default_page_types site property."""
    # Types which are not selectable as a default_page
    BASE_NON_DEFAULT_PAGE_TYPES = ['Folder',
                                   'Large Plone Folder',
                                   'Image',
                                   'File']

    propTool = getToolByName(portal, 'portal_properties', None)
    if propTool is not None:
        propSheet = getattr(propTool, 'site_properties', None)
        if propSheet is not None:
            if not propSheet.hasProperty('non_default_page_types'):
                propSheet.manage_addProperty('non_default_page_types',
                                             BASE_NON_DEFAULT_PAGE_TYPES,
                                             'lines')
            out.append("Added 'non_default_page_types' property to site_properties.")


def removePortalTabsActions(portal, out):
    """Remove portal_tabs actions"""
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        new_actions = actionsTool._cloneActions()
        for action in new_actions:
            if action.getId() in ['Members','news']:
                action.visible = 0
        actionsTool._actions = new_actions
        out.append("Disabled 'news' and 'Members' portal tabs actions.")


def addNewsFolder(portal, out):
    """Add news folder to portal root"""
    if 'news' not in portal.objectIds():
        _createObjectByType('Large Plone Folder', portal, id='news',
                            title='News', description='Site News')
        out.append("Added news folder.")
    news = getattr(aq_base(portal), 'news')

    # Enable ConstrainTypes and set to News
    addable_types = ['News Item']
    if getattr(news.aq_base, 'setConstrainTypesMode', None) is not None:
        news.setConstrainTypesMode(1)
        news.setImmediatelyAddableTypes(addable_types)
        news.setLocallyAllowedTypes(addable_types)
        out.append("Set constrain types for news folder.")

    # Add news_listing.pt as default page
    # property manager hasProperty can give odd results ask forgiveness instead
    try:
        news.manage_addProperty('default_page', ['news_topic','news_listing','index_html'], 'lines')
    except BadRequest:
        pass
    out.append("Added default view for news folder.")


def addEventsFolder(portal, out):
    """Add events folder to portal root"""
    if 'events' not in portal.objectIds():
        _createObjectByType('Large Plone Folder', portal, id='events',
                            title='Events', description='Site Events')
        out.append("Added events folder.")
    events = getattr(aq_base(portal), 'events')

    # Enable ConstrainTypes and set to Event
    addable_types = ['Event']
    if getattr(events.aq_base, 'setConstrainTypesMode', None) is not None:
        events.setConstrainTypesMode(1)
        events.setImmediatelyAddableTypes(addable_types)
        events.setLocallyAllowedTypes(addable_types)
        out.append("Set constrain types for events folder.")

    # Add events_listing.pt as default page
    # property manager hasProperty can give odd results ask forgiveness instead
    try:
        events.manage_addProperty('default_page', ['events_topic','events_listing','index_html'], 'lines')
    except BadRequest:
        pass
    out.append("Added default view for events folder.")


def addExclude_from_navMetadata(portal, out):
    """Adds the exclude_from_nav metadata."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        if 'exclude_from_nav' in catalog.schema():
            return 0
        catalog.addColumn('exclude_from_nav')
        out.append("Added 'exclude_from_nav' metadata to portal_catalog.")
        return 1 # Ask for reindexing
    return 0


def addEditContentActions(portal, out):
    """Add edit actions in content menu and
       move contents action to batch menu.
    """
    CATEGORY = 'object_buttons'
    ACTIONS = (
        {'id'        : 'delete',
         'name'      : 'Delete',
         'action'    : 'string:${object_url}/object_delete',
         'condition' : 'python:portal.portal_membership.checkPermission("Delete objects", object.aq_inner.aq_parent) and object is not portal.portal_url.getPortalObject()',
         'permission': CMFCorePermissions.DeleteObjects,
        },
        {'id'        : 'paste',
         'name'      : 'Paste',
         'action'    : 'string:${object_url}/object_paste',
         'condition' : 'folder/cb_dataValid',
         'permission': CMFCorePermissions.View,
        },
        {'id'        : 'copy',
         'name'      : 'Copy',
         'action'    : 'string:${object_url}/object_copy',
         'condition' : 'python:object is not portal.portal_url.getPortalObject()',
         'permission': CMFCorePermissions.Permissions.copy_or_move,
        },
        {'id'        : 'cut',
         'name'      : 'Cut',
         'action'    : 'string:${object_url}/object_cut',
         'condition' : 'python:portal.portal_membership.checkPermission("Delete objects", object.aq_inner.aq_parent) and object is not portal.portal_url.getPortalObject()',
         'permission': CMFCorePermissions.Permissions.copy_or_move,
        },
        {'id'        : 'batch',
         'name'      : 'Contents',
         'action'    : "python:((object.isDefaultPageInFolder() and object.getParentNode().absolute_url()) or folder_url)+'/folder_contents'",
         'condition' : 'python:folder.displayContentsTab()',
         'permission': CMFCorePermissions.View,
         'category'  : 'batch',
        },
    )

    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        # first we don't need old 'Contents' action anymore
        new_actions = actionsTool._cloneActions()
        for action in new_actions:
            if action.getId() == 'folderContents':
                action.visible = False
        actionsTool._actions = new_actions
        # then we add new actions
        for newaction in ACTIONS:
            for action in actionsTool.listActions():
                if action.getId() == newaction['id'] \
                        and action.getCategory() == newaction.get('category', CATEGORY) \
                    and action.getCondition() == newaction['condition']:
                    break # We already have the action
            else:
                actionsTool.addAction(newaction['id'],
                    name=newaction['name'],
                    action=newaction['action'],
                    condition=newaction['condition'],
                    permission=newaction['permission'],
                    category=newaction.get('category', CATEGORY),
                    visible=1)
            out.append("Added '%s' contentmenu action to actions tool." % newaction['name'])


def indexMembersFolder(portal, out):
    """Makes sure the Members folder is cataloged."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        membershipTool = getToolByName(portal, 'portal_membership', None)
        if membershipTool is not None:
            members = membershipTool.getMembersFolder()
            if members is not None:
                members.indexObject()
                out.append('Recataloged Members folder.')


def indexNewsFolder(portal, out):
    """Makes sure the News folder is cataloged."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        if hasattr(aq_base(portal), 'news'):
            portal.news.indexObject()
            out.append('Recataloged news folder.')


def indexEventsFolder(portal, out):
    """Makes sure the Events folder is cataloged."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        if hasattr(aq_base(portal), 'events'):
            portal.events.indexObject()
            out.append('Recataloged events folder.')


class Record:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def migrateDateIndexes(portal, out):
    """Converts FieldIndexes to DateIndexes."""
    DATEINDEXES = (
    'created',
    'modified',
    'Date',
    'start',
    'end',
    'effective',
    'expires',
    )

    changed = 0
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        for indexname in DATEINDEXES:
            try:
                index = catalog._catalog.getIndex(indexname)
            except KeyError:
                pass
            else:
                indextype = index.__class__.__name__
                if indextype == 'DateIndex':
                    continue
                catalog.delIndex(indexname)
                out.append("Deleted %s '%s'." % (indextype, indexname))

            catalog.addIndex(indexname, 'DateIndex')
            out.append("Added DateIndex '%s'." % indexname)
            changed = 1 # Ask for reindexing
    return changed


def migrateDateRangeIndexes(portal, out):
    """Creates new DateRangeIndexes."""
    DATERANGEINDEXES = (
    ('effectiveRange', 'effective', 'expires'),
    #('eventRange', 'start', 'end'),
    )

    changed = 0
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        for indexname, since, until in DATERANGEINDEXES:
            try:
                index = catalog._catalog.getIndex(indexname)
            except KeyError:
                pass
            else:
                indextype = index.__class__.__name__
                if indextype == 'DateRangeIndex':
                    continue
                catalog.delIndex(indexname)
                out.append("Deleted %s '%s'." % (indextype, indexname))

            extra = Record(since_field=since, until_field=until)
            catalog.addIndex(indexname, 'DateRangeIndex', extra)
            out.append("Added DateRangeIndex '%s' (%s, %s)." % (indexname, since, until))
            changed = 1 # Ask for reindexing
    return changed


def addSortable_TitleIndex(portal, out):
    """Adds the sortable_title FieldIndex."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        try:
            index = catalog._catalog.getIndex('sortable_title')
        except KeyError:
            pass
        else:
            indextype = index.__class__.__name__
            if indextype == 'FieldIndex':
                return 0
            catalog.delIndex('sortable_title')
            out.append("Deleted %s 'sortable_title' from portal_catalog." % indextype)

        catalog.addIndex('sortable_title', 'FieldIndex')
        out.append("Added FieldIndex 'sortable_title' to portal_catalog.")
        return 1 # Ask for reindexing
    return 0


def addIs_FolderishMetadata(portal, out):
    """Adds the is_folderish metadata."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        if 'is_folderish' in catalog.schema():
            return 0
        catalog.addColumn('is_folderish')
        out.append("Added 'is_folderish' metadata to portal_catalog.")
        return 1 # Ask for reindexing
    return 0


def addDefaultTypesToPortalFactory(portal, out):
    """Put the default content types in portal_factory"""
    factory = getToolByName(portal, 'portal_factory', None)
    if factory is not None:
        types = factory.getFactoryTypes().keys()
        for metaType in ('Document', 'Event', 'File', 'Folder', 'Image', 
                         'Folder', 'Large Plone Folder', 'Link', 'News Item',
                         'Topic'):
            if metaType not in types:
                types.append(metaType)
        factory.manage_setPortalFactoryTypes(listOfTypeIds = types)
        out.append('Added default content types to portal_factory.')


def addNewsTopic(portal, out):
    news = portal.news
    if 'news_topic' not in news.objectIds() and getattr(portal,'portal_atct', None) is not None:
        _createObjectByType('Topic', news, id='news_topic',
                            title='News', description='Site News')
        topic = news.news_topic
        type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
        type_crit.setValue('News Item')
        sort_crit = topic.addCriterion('created','ATSortCriterion')
        out.append('Added Topic for default news folder view.')
    else:
        out.append('Topic default news folder view already in place or ATCT is not installed.')


def addEventsTopic(portal, out):
    events = portal.events
    if 'events_topic' not in events.objectIds() and getattr(portal,'portal_atct', None) is not None:
        _createObjectByType('Topic', events, id='events_topic',
                            title='Events', description='Site Events')
        topic = events.events_topic
        type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
        type_crit.setValue('Event')
        sort_crit = topic.addCriterion('start','ATSortCriterion')
        out.append('Added Topic for default events folder view.')
    else:
        out.append('Topic default events folder view already in place or ATCT is not installed.')


def addDisableFolderSectionsSiteProperty(portal, out):
    """Adds disable_folder_sections site property."""
    # Boolean to disable using toplevel folders as tabs
    # users who turn this on may want to readd the Members and
    # News actions.
    propTool = getToolByName(portal, 'portal_properties', None)
    if propTool is not None:
        propSheet = getattr(propTool, 'site_properties', None)
        if propSheet is not None:
            if not propSheet.hasProperty('disable_folder_sections'):
                propSheet.manage_addProperty('disable_folder_sections',
                                             False,
                                             'boolean')
            out.append("Added 'disable_folder_sections' property to site_properties.")


def addSiteRootViewTemplates(portal, out):
    """Add default view templates to site root"""
    if not portal.hasProperty('selectable_views'):
        portal.manage_addProperty('selectable_views', 
                                  ['folder_listing',
                                   'news_listing'],
                                  'lines')
        out.append("Added 'selectable_views' property to portal root")


def addMemberdataHome_Page(portal, out):
    memberdata_tool = safeGetMemberDataTool(portal)
    if memberdata_tool is not None:
        if not memberdata_tool.hasProperty('home_page'):
            memberdata_tool.manage_addProperty('home_page', '', 'string')
            out.append("Added 'home_page' property to portal_memberdata.")

def addMemberdataLocation(portal, out):
    memberdata_tool = safeGetMemberDataTool(portal)
    if memberdata_tool is not None:
        if not memberdata_tool.hasProperty('location'):
            memberdata_tool.manage_addProperty('location', '', 'string')
            out.append("Added 'location' property to portal_memberdata.")

def addMemberdataDescription(portal, out):
    memberdata_tool = safeGetMemberDataTool(portal)
    if memberdata_tool is not None:
        if not memberdata_tool.hasProperty('description'):
            memberdata_tool.manage_addProperty('description', '', 'text')
            out.append("Added 'description' property to portal_memberdata.")

def addMemberdataLanguage(portal, out):
    memberdata_tool = safeGetMemberDataTool(portal)
    if memberdata_tool is not None:
        if not memberdata_tool.hasProperty('language'):
            memberdata_tool.manage_addProperty('language', '', 'string')
            out.append("Added 'language' property to portal_memberdata.")

def addMemberdataExtEditor(portal, out):
    memberdata_tool = safeGetMemberDataTool(portal)
    if memberdata_tool is not None:
        if not memberdata_tool.hasProperty('ext_editor'):
            memberdata_tool.manage_addProperty('ext_editor', '1', 'boolean')
            out.append("Added 'ext_editor' property to portal_memberdata.")

def alterChangeStateActionCondition(portal, out):
    """ Change the change_state action so that it checks either Modify portal
        content or Review portal content.
    """
    newaction = {'id'        : 'change_state',
                  'name'      : 'Change State',
                  'action'    : 'string:content_status_history:method',
                  'condition' : 'python:portal.portal_membership.checkPermission("Modify portal content", object) or portal.portal_membership.checkPermission("Review portal content", object)',
                  'permission': CMFCorePermissions.View,
                  'category': 'folder_buttons',
                }
    exists = False
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        new_actions = actionsTool._cloneActions()
        for action in new_actions:
            if action.getId() == 'change_state' and action.category == newaction['category']:
                exists = True
                if not action.condition:
                    action.permissions = (newaction['permission'],)
                    action.condition = Expression(text=newaction['condition']) or ''
                    out.append('Modified existing change_state action')
        if exists:
            actionsTool._actions = new_actions
        else:
            actionsTool.addAction(newaction['id'],
                    name=newaction['name'],
                    action=newaction['action'],
                    condition=newaction['condition'],
                    permission=newaction['permission'],
                    category=newaction['category'],
                    visible=1)
            out.append("Added missing change_state action")


def alterExtEditorActionCondition(portal, out):
    """ Change the extedit action so that it checks the user
    preferences for external editing.
    """
    newaction = {'id'        : 'extedit',
                  'name'      : 'Change State',
                  'action'    : 'string:$object_url/external_edit',
                  'condition' : 'python: member and hasattr(member, "ext_editor") and member.ext_editor and object.absolute_url() != portal_url',
                  'permission': CMFCorePermissions.ModifyPortalContent,
                  'category': 'document_actions',
                }
    exists = False
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        new_actions = actionsTool._cloneActions()
        for action in new_actions:
            if action.getId() == 'extedit' and action.category == newaction['category']:
                exists = True
                action.condition = Expression(text=newaction['condition']) or ''
                out.append('Modified existing extedit action')
        if exists:
            actionsTool._actions = new_actions
        else:
            actionsTool.addAction(newaction['id'],
                    name=newaction['name'],
                    action=newaction['action'],
                    condition=newaction['condition'],
                    permission=newaction['permission'],
                    category=newaction['category'],
                    visible=1)
            out.append("Added missing extedit action")


def fixFolderButtonsActions(portal, out):
    """ Change the copy and cut actions so that they check either more
        appropriate permissions.
    """
    CATEGORY = 'folder_buttons'
    ACTIONS = (
        {'id'        : 'copy',
         'name'      : 'Copy',
         'action'    : 'string:folder_copy:method',
         'condition' : '',
         'permission': CMFCorePermissions.Permissions.copy_or_move,
         'category' : 'folder_buttons',
        },
        {'id'        : 'cut',
         'name'      : 'Cut',
         'action'    : 'string:folder_cut:method',
         'condition': 'python:portal.portal_membership.checkPermission("Delete objects", object)',
         'permission': CMFCorePermissions.Permissions.copy_or_move,
         'category' : 'folder_buttons',
        },
    )
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        for newaction in ACTIONS:
            current_actions = actionsTool._cloneActions()
            exists = False
            for action in current_actions:
                if action.getId() == newaction['id'] and action.category == newaction['category']:
                    exists = True
                    if action.permissions != (
                            CMFCorePermissions.Permissions.copy_or_move,):
                        action.permissions = (newaction['permission'],)
                        action.condition = Expression(text=newaction['condition']) or ''
                        out.append('Modified existing %s action'%newaction['id'])
            if exists:
                actionsTool._actions = current_actions
            else:
                actionsTool.addAction(newaction['id'],
                    name=newaction['name'],
                    action=newaction['action'],
                    condition=newaction['condition'],
                    permission=newaction['permission'],
                    category=newaction['category'],
                    visible=1)
                out.append("Added missing %s action"%newaction['id'])


def addTypesUseViewActionInListingsProperty(portal, out):
    # Adds a typesUseViewActionInListings list property to site_properties
    # which is used to determine which types should use not immediate_view
    # in folder listings (and batch mode).  This is important for types like
    # Image and File.
    propTool = getToolByName(portal, 'portal_properties', None)
    if propTool is not None:
        propSheet = getattr(propTool, 'site_properties', None)
        if propSheet is not None:
            if not propSheet.hasProperty('typesUseViewActionInListings'):
                propSheet.manage_addProperty('typesUseViewActionInListings',
                                             ['Image','File'],
                                             'lines')
            out.append("Added 'typesUseViewActionInListings' property to site_properties.")


def switchToExpirationDateMetadata(portal, out):
    """Remove ExpiresDate and add ExpirationDate columns the catalog."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        schema = catalog.schema()
        if 'ExpiresDate' in schema:
            catalog.delColumn('ExpiresDate')
            out.append("Removed 'ExpiresDate' metadata from portal_catalog.")
        if 'ExpirationDate' in schema:
            return 0
        catalog.addColumn('ExpirationDate')
        out.append("Added 'ExpirationDate' metadata to portal_catalog.")
        return 1 # Ask for reindexing
    return 0


def changePloneSetupActionToSiteSetup(portal, out):
    """ Change the plone_setup action so that its title is Site Setup.
    """
    newaction = {'id': 'plone_setup',
                'name': 'Site Setup',
                'action': 'string: ${portal_url}/plone_control_panel',
                'condition': '', # condition
                'permission': CMFCorePermissions.ManagePortal,
                'category': 'user',
                'visible': 1}
    exists = False
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        new_actions = actionsTool._cloneActions()
        for action in new_actions:
            if action.getId() == newaction['id'] and action.category == newaction['category']:
                exists = True
                action.title = newaction['name']
                out.append('Modified existing plone_setup action')
        if exists:
            actionsTool._actions = new_actions
        else:
            actionsTool.addAction(newaction['id'],
                    name=newaction['name'],
                    action=newaction['action'],
                    condition=newaction['condition'],
                    permission=newaction['permission'],
                    category=newaction['category'],
                    visible=1)
            out.append("Added missing plone_setup action")


def changePloneSiteIcon(portal, out):
    """Change the icon for plone site from folder_icon to site_icon"""
    typesTool = getToolByName(portal, 'portal_types', None)
    if typesTool is not None:
        plone_FTI = getattr(typesTool, 'Plone Site', None)
        if plone_FTI is not None and plone_FTI.content_icon == 'folder_icon.gif':
            plone_FTI.content_icon = 'site_icon.gif'
            out.append("Changed Plone Site icon")

def migrateCatalogIndexes(portal, out):
    """Migrate catalog indexes if running under Zope 2.8"""
    from Products.ZCatalog.ZCatalog import ZCatalog
    migrated = False
    if not hasattr(ZCatalog, 'manage_convertIndexes'):
        return migrated
    FLAG = '_migrated_280'
    for obj in portal.objectValues():
        if not isinstance(obj, ZCatalog):
            continue
        if getattr(aq_base(obj), FLAG, False):
            continue
        out.append("Running manage_convertIndexes on "
                   "ZCatalog instance '%s'" % obj.getId())
        p_threshold = getattr(obj, 'pgthreshold', 0)
        obj.pgthreshold = 300
        obj.manage_convertIndexes()
        obj.pgthreshold = p_threshold
        out.append("Finished migrating catalog indexes "
                   "for ZCatalog instance '%s'" % obj.getId())
        migrated = True
    return migrated
