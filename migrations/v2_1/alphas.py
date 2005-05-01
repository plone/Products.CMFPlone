import os

from Acquisition import aq_base
from zExceptions import BadRequest
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct


def two05_alpha1(portal):
    """2.0.5 -> 2.1-alpha1
    """
    out = []

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

    return out


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

    # Switch path index to ExtendedPathIndex
    reindex += switchPathIndex(portal, out)

    # Add getObjPositionInParent index
    reindex += addGetObjPositionInParentIndex(portal, out)

    # Add getObjSize support to catalog
    reindex += addGetObjSizeMetadata(portal, out)

    # Update navtree_properties
    updateNavTreeProperties(portal, out)

    # Add sitemap action
    addSitemapAction(portal, out)

    # Install CSS and Javascript registries
    # also install default CSS and JS in the registry tools
    installCSSandJSRegistries(portal, out)

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

    # Add exclude_from_nav index
    reindex += addExclude_from_navMetadata(portal, out)

    # Add objec cut/copy/paste/delete + batch buttons
    addEditContentActions(portal, out)

    # Install DateIndexes and DateRangeIndexes
    reindex += migrateDateIndexes(portal, out)
    reindex += migrateDateRangeIndexes(portal, out)

    # Add sortable_title index
    reindex += addSortable_TitleIndex(portal, out)

    # add is_folderish metadata
    reindex += addIs_FolderishMetadata(portal, out)

    # Add groups 'administrators' and 'reviewers'
    addDefaultGroups(portal, out)

    # Put default types in portal_factory
    addDefaultTypesToPortalFactory(portal, out)

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

    # Add non_default_page_types site property
    addDisableFolderSectionsSiteProperty(portal, out)

    # Add selectable_views to portal root
    addSiteRootViewTemplates(portal, out)

    return out


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
    get_transaction().commit(1)
    migrateFromCMFtoATCT = portal.migrateFromCMFtoATCT
    switchCMF2ATCT = portal.switchCMF2ATCT
    #out.append('Migrating and switching to ATContentTypes ...')
    result = migrateFromCMFtoATCT()
    out.append(result)
    try:
        switchCMF2ATCT(skip_rename=False)
    except IndexError:
        switchCMF2ATCT(skip_rename=True)
    get_transaction().commit(1)
    #out.append('Switched portal to ATContentTypes.')


def migrateToATCT10(portal, out):
    """Switches portal to ATCT 1.0
    """
    get_transaction().commit(1)
    tool = portal.portal_atct
    tool.migrateToATCT()
    get_transaction().commit(1)


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
    memberdata = getToolByName(portal, 'portal_memberdata', None)
    if memberdata is not None:
        if memberdata.hasProperty('visible_ids'):
            memberdata.manage_delProperties(['visible_ids'])
        out.append("Deleted 'visible_ids' property from portal_memberdata.")


def deleteFormToolTipsMemberProperty(portal, out):
    """Deletes formtooltips memberdata property."""
    memberdata = getToolByName(portal, 'portal_memberdata', None)
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
                propSheet._setProperty('sortAttribute', 'getObjPositionInParent', 'string')
                propSheet._setProperty('sortOrder', 'asc', 'string')
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
    if groupsTool is not None:
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
        catalog.threshold = 2000
        catalog.refreshCatalog(clear=1)
        catalog.threshold = old_threshold
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
            cssreg.registerStylesheet('plonePresentation.css', media='presentation')
            cssreg.registerStylesheet('plonePrint.css', media='print')
            cssreg.registerStylesheet('ploneMobile.css', media='handheld')
            cssreg.registerStylesheet('ploneColumns.css')
            cssreg.registerStylesheet('ploneAuthoring.css')
            cssreg.registerStylesheet('plonePublic.css')
            cssreg.registerStylesheet('ploneBase.css')
            cssreg.registerStylesheet('ploneCustom.css')
            cssreg.registerStylesheet('ploneRTL.css', expression="python:object.isRightToLeft(domain='plone')")

        jsreg = getToolByName(portal, 'portal_javascripts', None)
        if jsreg is not None:
            jsreg.clearScripts()
            jsreg.registerScript('vcXMLRPC.js', enabled=False)
            jsreg.registerScript('correctPREformatting.js', enabled=False)
            jsreg.registerScript('plone_minwidth.js' , enabled=False)
            jsreg.registerScript('sarissa.js')
            jsreg.registerScript('calendar_formfield.js')
            jsreg.registerScript('ie5fixes.js')
            jsreg.registerScript('calendarpopup.js')
            jsreg.registerScript('collapsiblesections.js')
            jsreg.registerScript('first_input_focus.js')
            jsreg.registerScript('folder_contents_filter.js')
            jsreg.registerScript('fullscreenmode.js')
            jsreg.registerScript('highlightsearchterms.js')
            jsreg.registerScript('mark_special_links.js')
            jsreg.registerScript('select_all.js')
            jsreg.registerScript('styleswitcher.js')
            jsreg.registerScript('livesearch.js')
            jsreg.registerScript('table_sorter.js')
            jsreg.registerScript('plone_menu.js')
            jsreg.registerScript('cookie_functions.js')
            jsreg.registerScript('nodeutilities.js')
            jsreg.registerScript('plone_javascript_variables.js')
            jsreg.registerScript('register_function.js')

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
        i = 0
        to_delete = []
        for action in actionsTool.listActions():
            if action.getId() in ['Members','news'] and action.getCategory() == 'portal_tabs':
                to_delete.append(i)
            i += 1
        if to_delete:
            actionsTool.deleteActions(to_delete)
        out.append("Deleted old portal_tabs actions.")


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
         'name'      : 'Batch Mode',
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
                action.visible = 0
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