import os, string
from Acquisition import aq_base
from zExceptions import BadRequest
from Products.CMFCore.permissions import AccessInactivePortalContent, \
     DeleteObjects, ListFolderContents, ManagePortal, ModifyPortalContent, View
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct, \
     safeGetMemberDataTool, safeEditProperty, cleanupSkinPath
from Products.CMFCore.DirectoryView import createDirectoryView
from alphas import reindexCatalog, indexMembersFolder, indexNewsFolder, \
                    indexEventsFolder, convertPloneFTIToCMFDynamicViewFTI
from Products.CMFPlone.PloneTool import AllowSendto
from Products.CMFPlone.migrations.v2_1.alphas import migrateResourceRegistries

def alpha2_beta1(portal):
    """2.1-alpha2 -> 2.1-beta1
    """
    out = []
    reindex = 0

    #Make object paste action work with all default pages.
    fixObjectPasteActionForDefaultPages(portal, out)

    # Make batch action a toggle by using a pair of actions
    fixBatchActionToggle(portal, out)

    # Update the 'my folder' action to not use folder_contents
    fixMyFolderAction(portal, out)

    # Migrate ResourceRegistries
    # This is also done in alpha migrations, but that was introduced later, so
    # it has to be called here as well or migrations from alphas might break.
    migrateResourceRegistries(portal, out)

    # Bring ploneRTL back to the nearly-top of the stack
    reorderStylesheets(portal, out)

    # Grant Access inactive portal content to Owner
    allowOwnerToAccessInactiveContent(portal, out)

    # Add criteria to News and Events topics to restrict to published
    restrictNewsTopicToPublished(portal, out)
    restrictEventsTopicToPublished(portal, out)

    # Install new login skins and scripts
    installLogin(portal, out)

    # Install kupu
    installKupu(portal, out)

    # Add the stylesheets for font size the selector
    addFontSizeStylesheets(portal, out)

    # Add cssQuery.js
    addCssQueryJS(portal, out)

    # Exchange plone_menu.js with dropdown.js
    exchangePloneMenuWithDropDown(portal, out)

    # Remove plone prefix of stylesheet files
    removePlonePrefixFromStylesheets(portal, out)

    # Convert navtree whitelist to blacklist
    convertNavTreeWhitelistToBlacklist(portal, out)

    # Add Index for is_default_page
    reindex += addIsDefaultPageIndex(portal, out)

    # Add Index for is_foldersh and remove corresponding metadata
    reindex += addIsFolderishIndex(portal, out)

    # Add the plone_3rdParty to the skin layers
    add3rdPartySkinPath(portal, out)

    # Add deprecated and portlet style sheets
    addDeprecatedAndPortletStylesheets(portal, out)

    # Add LiveSearch site property
    addEnableLivesearchProperty(portal, out)

    # Add icon for search settings configlet
    addIconForSearchSettingsConfiglet(portal,out)

    # CMF 1.5 Cookie Crumbler has new properties
    sanitizeCookieCrumbler(portal, out)

    # Fix folderlisting action for portal
    fixFolderlistingAction(portal, out)

    # ADD NEW STUFF BEFORE THIS LINE AND LEAVE THE TRAILER ALONE!

    # Rebuild catalog
    if reindex:
        reindexCatalog(portal, out)

    return out


def beta1_beta2(portal):
    """2.1-beta1 -> 2.1-beta2
    """
    out = []
    reindex = 0

    # Convert Plone Site FTI to CMFDynamicViewFTI again, for people already on
    # an alpha or beta.
    convertPloneFTIToCMFDynamicViewFTI(portal, out)

    # Fix folderlisting action for portal
    fixFolderContentsActionAgain(portal, out)

    # Change the actions on the Portal FTI to category 'object' in order to
    # get consistent tab ordering across the portal.
    changePortalActionCategory(portal, out)

    # Add method aliases for PloneSite
    addMethodAliasesForPloneSite(portal, out)

    # Add 'Large Plone Folder' to the list of types not to query for the
    # navtree
    updateParentMetaTypesNotToQuery(portal, out)

    # Fix condition on External Editor action
    fixExtEditAction(portal, out)

    # Disable external editor member property by default
    changeMemberdataExtEditor(portal, out)

    # Fix Workflow state titles
    fixWorkflowStateTitles(portal, out)

    # Remove the text size actions, add contact and accessibility actions, and
    # move site setup to site_actions
    changeSiteActions(portal, out)

    # Remove the oddly located plone_membership plone_setup action
    removePloneSetupActionFromPortalMembership(portal, out)

    # Make sure our 'view' alises are (selected layout)
    fixViewMethodAliases(portal, out)

    # Make portal root use /edit and /sharing URLs on actions
    fixPortalEditAndSharingActions(portal, out)

    # Add CMFUid tools
    addCMFUidTools(portal, out)

    # Correct CSS media types
    fixCSSMediaTypes(portal,out)

    # Add properties for filtering the navtree/sitemap by workflow state
    addWFStateFilteringToNavTree(portal, out)

    # Add icon for navigation settings configlet
    addIconForNavigationSettingsConfiglet(portal,out)

    # Be sure that Search and Navigation panels are installed
    addSearchAndNavigationConfiglets(portal, out)

    # add formsubmithelpers.js to ResourceRegistries
    addFormSubmitHelpersJS(portal, out)

    # Re-Add the memberdata property for visible ids
    readdVisibleIdsMemberProperty(portal, out)

    # Add CMF types to blacklists
    addCMFTypesToSearchBlackList(portal, out)

    # Convert default page types to whitelist
    convertDefaultPageTypesToWhitelist(portal, out)

    # setup new Allow Sendto permission
    setupAllowSendtoPermission(portal, out)

    # FIXME: *Must* be called after reindexCatalog.
    # In tests, reindexing loses the folders for some reason...

    # Make sure the Members folder is cataloged
    indexMembersFolder(portal, out)

    # Make sure the News folder is cataloged
    indexNewsFolder(portal, out)

    # Make sure the Events folder is cataloged
    indexEventsFolder(portal, out)

    return out


def installLogin(portal, out):
    # register new login scripts
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    if jsreg is not None:
        if not 'login.js' in jsreg.getResourceIds():
            jsreg.registerScript('login.js')
            out.append('Registered login.js')

    # register login skin
    st = getToolByName(portal, 'portal_skins')
    if not hasattr(aq_base(st), 'plone_login'):
        createDirectoryView(st, os.path.join('CMFPlone', 'skins', 'plone_login'))
        out.append('Added directory view for plone_login')

    # add login skin to Plone Default, Plone Tableless skins
    skins = ['Plone Default', 'Plone Tableless']
    selections = st._getSelections()
    for s in skins:
        if not selections.has_key(s):
           continue
        cleanupSkinPath(portal, s)
        path = st.getSkinPath(s)
        path = map(string.strip, string.split(path,','))
        if not 'plone_login' in path:
            if 'cmf_legacy' in path:
                path.insert(path.index('cmf_legacy'), 'plone_login')
            else:
                path.append('plone_login')
            st.addSkinSelection(s, ','.join(path))
            out.append('Added plone_login to %s' % s)

    # add a property to control whether or not "user name not found" message
    # should be displayed on login failure
    propTool = getToolByName(portal, 'portal_properties', None)
    if propTool is not None:
        propSheet = getattr(propTool, 'site_properties', None)
        if propSheet is not None:
            if not propSheet.hasProperty('verify_login_name'):
                propSheet.manage_addProperty('verify_login_name', 1, 'boolean')
            out.append("Added 'verify_login_name' property to site_properties.")


def fixObjectPasteActionForDefaultPages(portal, out):
    """ Fix the object paste action so that paste into default pages pastes
        into the parent.
    """
    newaction =  {'id'        : 'paste',
                  'name'      : 'Paste',
                  'action'    : 'python:"%s/object_paste"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)',
                  'condition' : 'folder/cb_dataValid',
                  'permission': View,
                  'category': 'object_buttons',
                 }
    exists = False
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        new_actions = actionsTool._cloneActions()
        for action in new_actions:
            if action.getId() == newaction['id'] and action.category == newaction['category']:
                exists = True
                action.setActionExpression(Expression(newaction['action']))
                out.append('Modified existing object paste action for folderish default pages')
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
            out.append("Added missing object paste action")

def fixBatchActionToggle(portal, out):
    """Fix batch actions so as to function as a toggle
    """
    ACTIONS = (
        {'id'        : 'batch',
         'name'      : 'Contents',
         'action'    : "python:((object.isDefaultPageInFolder() and object.getParentNode().absolute_url()) or folder_url)+'/folder_contents'",
         'condition' : "python:portal.portal_membership.checkPermission('View',folder) and folder.displayContentsTab() and object.REQUEST['ACTUAL_URL'] != object.absolute_url() + '/folder_contents'",
         'permission': View,
         'category'  : 'batch',
        },
        {'id'        : 'nobatch',
         'name'      : 'Default view',
         'action'    : "string:${folder_url}/view",
         'condition' : "python:portal.portal_membership.checkPermission('View',folder) and folder.displayContentsTab() and object.REQUEST['ACTUAL_URL'] == object.absolute_url() + '/folder_contents'",
         'permission': View,
         'category'  : 'batch',
        },
    )

    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        # update/add actions
        for newaction in ACTIONS:
            idx = 0
            for action in actionsTool.listActions():
                # if action exists, remove and re-add
                if action.getId() == newaction['id'] \
                        and action.getCategory() == newaction['category']:
                    actionsTool.deleteActions((idx,))
                    break
                idx += 1
                
            actionsTool.addAction(newaction['id'],
                name=newaction['name'],
                action=newaction['action'],
                condition=newaction['condition'],
                permission=newaction['permission'],
                category=newaction['category'],
                visible=1)
                    
            out.append("Added '%s' contentmenu action to actions tool." % newaction['name'])

def fixMyFolderAction(portal, out):
    """Fix my folder action to point to folder w/o folder_contents
    """
    actionsTool = getToolByName(portal, 'portal_membership', None)
    if actionsTool is not None:
        for action in actionsTool.listActions():
            if action.getId() == 'mystuff' and action.getCategory() == 'user':
                action.setActionExpression(Expression('string:${portal/portal_membership/getHomeUrl}'))
                out.append("Made the 'mystuff' action point to folder listing instead of folder_contents")
                break


def reorderStylesheets(portal, out):
    """ Fix the position of the ploneRTL and member.css stylesheet

    After the 'alphas' migration, ploneRTL was at the bottom of the
    pile - it should be near the top in order to overwrite common
    plone stuff (which is left-to-right) for right-to-left (hebrew,
    arabic, etc.) usage.

    ploneMember.css breaks some stylesheet-combining order, so we're
    moving it to the bottom of the list.
    """
    qi = getToolByName(portal, 'portal_quickinstaller', None)
    if qi is not None:
        if not qi.isProductInstalled('ResourceRegistries'):
            qi.installProduct('ResourceRegistries', locked=0)
        cssreg = getToolByName(portal, 'portal_css', None)
        if cssreg is not None:
            stylesheet_ids = cssreg.getResourceIds()
            # Failsafe: first make sure the two stylesheets exist in the list
            if 'ploneRTL.css' not in stylesheet_ids:
                cssreg.registerStylesheet('ploneRTL.css',
                                           expression="python:object.isRightToLeft(domain='plone')")
            if 'ploneCustom.css' not in stylesheet_ids:
                cssreg.registerStylesheet('ploneCustom.css')
            if 'ploneMember.css' not in stylesheet_ids:
                cssreg.registerStylesheet('ploneMember.css',
                                           expression='not: portal/portal_membership/isAnonymousUser')
            # Now move 'em
            cssreg.moveResourceBefore('ploneRTL.css', 'ploneCustom.css')
            cssreg.moveResourceToTop('ploneMember.css')

def addCssQueryJS(portal, out):
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    if jsreg is not None:
        script_ids = jsreg.getResourceIds()
        # Failsafe: first make sure the stylesheet doesn't exist in the list
        if 'cssQuery.js' not in script_ids:
            jsreg.registerScript('cssQuery.js')
            try:
                jsreg.moveResourceBefore('cssQuery.js', 'plone_javascript_variables.js')
            except ValueError:
                try:
                    jsreg.moveResourceBefore('cssQuery.js', 'register_function.js')
                except ValueError:
                    # ok put to the top
                    jsreg.moveResourceToTop('cssQuery.js')

def exchangePloneMenuWithDropDown(portal, out):
    qi = getToolByName(portal, 'portal_quickinstaller', None)
    if qi is not None:
        if not qi.isProductInstalled('ResourceRegistries'):
            qi.installProduct('ResourceRegistries', locked=0)
        jsreg = getToolByName(portal, 'portal_javascripts', None)
        if jsreg is not None:
            script_ids = jsreg.getResourceIds()
            # Failsafe: first make sure the stylesheet doesn't exist in the list
            if 'dropdown.js' not in script_ids:
                jsreg.registerScript('dropdown.js')
                if 'plone_menu.js' in script_ids:
                    jsreg.moveResourceBefore('dropdown.js', 'plone_menu.js')
                    jsreg.unregisterResource('plone_menu.js')
                elif 'sarissa.js' in script_ids:
                    jsreg.moveResourceBefore('dropdown.js', 'sarissa.js')
                else:
                    # ok we stay at the bottom
                    pass

def removePlonePrefixFromStylesheets(portal, out):
    out.append("Removing plone prefix from stylesheets.")
    names = [
        ('ploneAuthoring.css', 'authoring.css'),
        ('ploneBase.css', 'base.css'),
        ('ploneColumns.css', 'columns.css'),
        ('ploneDeprecated.css', 'deprecated.css'),
        ('ploneGenerated.css', 'generated.css'),
        ('ploneIEFixes.css', 'IEFixes.css'),
        ('ploneMember.css', 'member.css'),
        ('ploneMobile.css', 'mobile.css'),
        ('ploneNS4.css', 'NS4.css'),
        ('plonePresentation.css', 'presentation.css'),
        ('plonePrint.css', 'print.css'),
        ('plonePublic.css', 'public.css'),
        ('ploneRTL.css', 'RTL.css'),
        ('ploneTextHuge.css', 'textHuge.css'),
        ('ploneTextLarge.css', 'textLarge.css'),
        ('ploneTextSmall.css', 'textSmall.css'),
    ]
    cssreg = getToolByName(portal, 'portal_css', None)
    if cssreg is not None:
        stylesheet_ids = cssreg.getResourceIds()
        for old, new in names:
            if old in stylesheet_ids:
                if new in stylesheet_ids:
                    # delete the old name
                    cssreg.unregisterResource(old)
                else:
                    # rename
                    cssreg.renameResource(old, new)
    else:
        out.append("No CSSRegistry found.")
    out.append("Finished removing plone prefix from stylesheets.")

def addDeprecatedAndPortletStylesheets(portal, out):
    out.append("Adding Portlet and Deprecated stylesheets.")
    cssreg = getToolByName(portal, 'portal_css', None)
    if cssreg is not None:
        stylesheet_ids = cssreg.getResourceIds()
        stylesheets_to_move_after = ('base.css', 'public.css', 'authoring.css', 'member.css')
        if 'deprecated.css' not in stylesheet_ids:
            cssreg.registerStylesheet('deprecated.css', media="screen")
            for style_id in stylesheets_to_move_after:
                if style_id in stylesheet_ids:
                    # found an existing stylesheet, place the new one below
                    cssreg.moveResourceAfter('deprecated.css', style_id)
                    break # we are done
        if 'portlets.css' not in stylesheet_ids:
            cssreg.registerStylesheet('portlets.css', media="screen")
            cssreg.moveResourceAfter('portlets.css', 'deprecated.css')
    else:
        out.append("No CSSRegistry found.")
    out.append("Finished adding Portlet and Deprecated stylesheets.")

def allowOwnerToAccessInactiveContent(portal, out):
    permission = AccessInactivePortalContent
    cur_perms=portal.permission_settings(permission)[0]
    roles = portal.valid_roles()
    if 'Owner' in roles:
        cur_allowed = [roles[i] for i in range(len(cur_perms['roles'])) if cur_perms['roles'][i]['checked']]
        if 'Owner' not in cur_allowed:
            cur_allowed.append('Owner')
            acquire = cur_perms['acquire'] and 1 or 0
            portal.manage_permission(permission, tuple(cur_allowed),
                                                        acquire=acquire)
            out.append('Granted "Access inactive portal content" permission to Owner role')


def restrictNewsTopicToPublished(portal, out):
    news = getattr(portal,'news', None)
    topic = getattr(news,'news_topic', None)
    if topic is not None:
        crit = getattr(topic, 'crit__review_state_ATSimpleStringCriterion', None)
        if crit is None:
            state_crit = topic.addCriterion('review_state',
                                                 'ATSimpleStringCriterion')
            state_crit.setValue('published')
            out.append('Added published criterion to news topic.')
        else:
            out.append('News topic already restricted to published.')
    else:
        out.append('News topic view not in place!')


def restrictEventsTopicToPublished(portal, out):
    events = getattr(portal,'events', None)
    topic = getattr(events,'events_topic', None)
    if topic is not None:
        crit = getattr(topic, 'crit__review_state_ATSimpleStringCriterion', None)
        if crit is None:
            state_crit = topic.addCriterion('review_state',
                                                 'ATSimpleStringCriterion')
            state_crit.setValue('published')
            out.append('Added published criterion to events topic.')
        else:
            out.append('Events topic already restricted to published.')
    else:
        out.append('Events topic view not in place!')


def installKupu(portal, out):
    """Quickinstalls Kupu if not installed yet."""
    # Kupu is optional
    try:
        import Products.kupu
    except ImportError:
        pass
    else:
        # Kupu is not installed by e.g. tests
        if 'kupu' in portal.Control_Panel.Products.objectIds():
            installOrReinstallProduct(portal, 'kupu', out)
            # Make kupu the default
            md = safeGetMemberDataTool(portal)
            if md and not hasattr(md, 'wysiwyg_editor'):
                safeEditProperty(md, 'wysiwyg_editor', 'Kupu', 'string')
            out.append('Set Kupu as default WYSIWYG editor.')


def addFontSizeStylesheets(portal, out):
    """Add the stylesheets for font size the selector."""
    cssreg = getToolByName(portal, 'portal_css', None)
    if cssreg is not None:
        stylesheet_ids = cssreg.getResourceIds()
        # Failsafe: first make sure the stylesheets don't exist in the list
        if 'ploneTextSmall.css' not in stylesheet_ids:
            cssreg.registerStylesheet('ploneTextSmall.css',
                                      media='screen',
                                      rel='alternate stylesheet',
                                      title='Small Text',
                                      rendering='link')
            if 'ploneRTL.css' in stylesheet_ids:
                cssreg.moveResourceBefore('ploneTextSmall.css', 'ploneRTL.css')
            out.append('Added ploneTextSmall.css to CSSRegistry.')
        if 'ploneTextLarge.css' not in stylesheet_ids:
            cssreg.registerStylesheet('ploneTextLarge.css',
                                      media='screen',
                                      rel='alternate stylesheet',
                                      title='Large Text',
                                      rendering='link')
            if 'ploneRTL.css' in stylesheet_ids:
                cssreg.moveResourceBefore('ploneTextLarge.css', 'ploneRTL.css')
            out.append('Added ploneTextLarge.css to CSSRegistry.')


def add3rdPartySkinPath(portal, out):
    """Add the plone_3rdParty to the skin layers."""
    skinsTool = getToolByName(portal, 'portal_skins', None)
    if skinsTool is not None:
        skins = ['Plone Default', 'Plone Tableless']
        selections = skinsTool._getSelections()
        for skin in skins:
            if not selections.has_key(skin):
               continue
            cleanupSkinPath(portal, skin)
            path = skinsTool.getSkinPath(skin)
            path = map(string.strip, string.split(path,','))
            if not 'plone_3rdParty' in path:
                if 'cmf_legacy' in path:
                    path.insert(path.index('cmf_legacy'), 'plone_3rdParty')
                else:
                    path.append('plone_3rdParty')
                skinsTool.addSkinSelection(skin, ','.join(path))
                out.append('Added plone_3rdParty to %s.' % skin)


def addEnableLivesearchProperty(portal, out):
    """Adds sitewide config for Livesearch."""
    propTool = getToolByName(portal, 'portal_properties', None)
    if propTool is not None:
        propSheet = getattr(aq_base(propTool), 'site_properties', None)
        if propSheet is not None:
            if not propSheet.hasProperty('enable_livesearch'):
                propSheet.manage_addProperty('enable_livesearch', 1, 'boolean')
            out.append("Added 'enable_livesearch' property to site_properties.")


def addIconForSearchSettingsConfiglet(portal, out):
    """Adds an icon for the search settings configlet. """
    iconsTool = getToolByName(portal, 'portal_actionicons', None)
    if iconsTool is not None:
        for icon in iconsTool.listActionIcons():
            if icon.getActionId() == 'SearchSettings':
                break # We already have the icon
        else:
            iconsTool.addActionIcon(
                category='controlpanel',
                action_id='SearchSettings',
                icon_expr='search_icon.gif',
                title='Search Settings',
                )
        out.append("Added 'search' icon to actionicons tool.")


def sanitizeCookieCrumbler(portal, out):
    """CMF 1.5 Cookie Crumbler handles the require login nonsense just fine."""
    cc = getToolByName(portal, 'cookie_authentication', None)
    if cc is not None:
        if cc.hasProperty('unauth_page'):
            cc._updateProperty('auto_login_page', 'login_form')
            out.append("Set 'Login page ID' of Cookie Crumbler to 'login_form'.")
            cc._updateProperty('unauth_page', 'insufficient_privileges')
            out.append("Set 'Failed authorization page ID' of Cookie Crumbler to 'insufficient_privileges'.")


def convertNavTreeWhitelistToBlacklist(portal, out):
    """Makes navtree_properties typesToList typesNotToList with appropriate
       conversion."""
    bl = ['ATBooleanCriterion',
          'ATCurrentAuthorCriterion',
          'ATPathCriterion',
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
    types_dict={}
    propTool = getToolByName(portal, 'portal_properties', None)
    typesTool = getToolByName(portal, 'portal_types', None)
    if propTool is not None:
        propSheet = getattr(aq_base(propTool), 'navtree_properties', None)
        sitepropSheet = getattr(aq_base(propTool), 'site_properties', None)
        if propSheet is not None:
            if propSheet.hasProperty('typesToList'):
                propSheet.manage_delProperties(['typesToList'])
                out.append('Removed navtree whitelist')
            if propSheet.hasProperty('typesNotToList'):
                propSheet.manage_delProperties(['typesNotToList'])
                out.append('Removed old navtree blacklist')
            if sitepropSheet is not None:
                bl = sitepropSheet.getProperty('types_not_searched', bl)
                # Let's add the two new criteria to the not searched list as well
                if 'ATCurrentAuthorCriterion' not in bl:
                    bl= bl + ('ATCurrentAuthorCriterion','ATPathCriterion')
                    sitepropSheet.manage_changeProperties(types_not_searched=bl)
                    out.append('Added new entries to "types_not_searched" site_property')
            if not propSheet.hasProperty('metaTypesNotToList'):
                propSheet._setProperty('metaTypesNotToList', bl, 'lines')
                out.append('Added navtree blacklist')
            else:
                # Combine existing values with not searchable types
                bl2 = propSheet.getProperty('metaTypesNotToList')
                if isinstance(bl2,basestring): bl2 = [bl2]
                for i in tuple(bl)+tuple(bl2):
                    types_dict[i] = True
                propSheet.manage_delProperties(['metaTypesNotToList'])
                propSheet._setProperty('metaTypesNotToList', types_dict.keys(),'lines')
                out.append('Updated navtree blacklist')


def addIsDefaultPageIndex(portal, out):
    """Adds the is_default_page FieldIndex."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        try:
            index = catalog._catalog.getIndex('is_default_page')
        except KeyError:
            pass
        else:
            indextype = index.__class__.__name__
            if indextype == 'FieldIndex':
                return 0
            catalog.delIndex('is_default_page')
            out.append("Deleted %s 'is_default_page' from portal_catalog." % indextype)

        catalog.addIndex('is_default_page', 'FieldIndex')
        out.append("Added FieldIndex 'is_default_page' to portal_catalog.")
        return 1 # Ask for reindexing
    return 0

# now used in rcs
def fixContentActionConditions(portal,out):
    """Don't use aq_parent in action conditions directly, as it will fail if
       we don't have permissions on the parent"""
    ACTIONS = (
        {'id'        : 'cut',
         'name'      : 'Cut',
         'action'    : 'python:"%s/object_cut"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)',
         'condition' : 'python:portal.portal_membership.checkPermission("Delete objects", object.aq_inner.getParentNode()) and portal.portal_membership.checkPermission("Copy or Move", object) and object is not portal and not (object.isDefaultPageInFolder() and object.getParentNode() is portal)',
         'permission': DeleteObjects,
         'category'  : 'object_buttons',
        },
        {'id'        : 'paste',
         'name'      : 'Paste',
         'action'    : 'python:"%s/object_paste"%((object.isDefaultPageInFolder() or not object.is_folderish()) and object.getParentNode().absolute_url() or object_url)',
         'condition' : 'folder/cb_dataValid|nothing',
         'permission': View,
         'category'  : 'object_buttons',
        },
        {'id'        : 'delete',
         'name'      : 'Delete',
         'action'    : 'python:"%s/object_delete"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)',
         'condition' : 'python:portal.portal_membership.checkPermission("Delete objects", object.aq_inner.getParentNode()) and object is not portal and not (object.isDefaultPageInFolder() and object.getParentNode() is portal)',
         'permission': DeleteObjects,
         'category'  : 'object_buttons',
        },
        {'id'        : 'copy',
         'name'      : 'Copy',
         'action'    : 'python:"%s/object_copy"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)',
         'condition' : 'python: portal.portal_membership.checkPermission("Copy or Move", object) and object is not portal and not (object.isDefaultPageInFolder() and object.getParentNode() is portal)',
         'permission': View,
         'category'  : 'object_buttons',
        },)

    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        # update/add actions
        for newaction in ACTIONS:
            idx = 0
            for action in actionsTool.listActions():
                # if action exists, remove and re-add
                if action.getId() == newaction['id'] \
                        and action.getCategory() == newaction['category']:
                    actionsTool.deleteActions((idx,))
                    break
                idx += 1

            actionsTool.addAction(newaction['id'],
                name=newaction['name'],
                action=newaction['action'],
                condition=newaction['condition'],
                permission=newaction['permission'],
                category=newaction['category'],
                visible=1)

            out.append("Added '%s' contentmenu action to actions tool." % newaction['name'])


def addIsFolderishIndex(portal, out):
    """Adds the is_folderish FieldIndex and removes the metadata."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        if 'is_folderish' in catalog.schema():
            catalog.delColumn('is_folderish')
            out.append("Removed metadata 'is_folderish' from portal_catalog.")
        try:
            index = catalog._catalog.getIndex('is_folderish')
        except KeyError:
            pass
        else:
            indextype = index.__class__.__name__
            if indextype == 'FieldIndex':
                return 0
            catalog.delIndex('is_folderish')
            out.append("Deleted %s 'is_folderish' from portal_catalog." % indextype)

        catalog.addIndex('is_folderish', 'FieldIndex')
        out.append("Added FieldIndex 'is_folderish' to portal_catalog.")
        return 1 # Ask for reindexing
    return 0

def fixFolderlistingAction(portal, out):
    """Fixes the folder listing action for portal to make it
       work properly with the new browser default magic
    """
    typesTool = getToolByName(portal, 'portal_types', None)
    if typesTool is not None:
        siteFTI = getattr(typesTool, 'Plone Site', None)
        if siteFTI is not None:
            haveFolderListing = False
            for action in siteFTI.listActions():
                if action.getId() == 'folderlisting':
                    action.setActionExpression(Expression('string:${folder_url}/view'))
                    action.condition = ''
                    haveFolderListing = True
                    break
            if not haveFolderListing:
                siteFTI.addAction('folderlisting',
                                    'Folder view',
                                    'string:${folder_url}/view',
                                    '',
                                    'View',
                                    'folder',
                                    visible=0)
            out.append("Set target expresion of folderlisting action for 'Plone Site' to 'view'")


def fixFolderContentsActionAgain(portal, out):
    """Remove batch toggle actions and replace folder_contents action
    """
    REMOVE_ACTIONS=('batch','nobatch')
    REMOVE_CATEGORY='batch'
    ACTIONS = (
        {'id'        : 'folderContents',
         'name'      : 'Contents',
         'action'    : "python:((object.isDefaultPageInFolder() and object.getParentNode().absolute_url()) or folder_url)+'/folder_contents'",
         'condition' : "object/displayContentsTab",
         'permission': ListFolderContents,
         'category'  : 'object',
        },
    )

    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        # First delete the batch toggle actions
        idx = 0
        del_idxs=[]
        for action in actionsTool.listActions():
            if action.getId() in REMOVE_ACTIONS \
                    and action.getCategory() == REMOVE_CATEGORY:
                del_idxs.append(idx)
            idx += 1
        actionsTool.deleteActions(del_idxs)

        # Now Remove and readd the contents action
        for newaction in ACTIONS:
            idx = 0
            del_idxs=[]
            for action in actionsTool.listActions():
                # if action exists, remove (including duplicates)
                if action.getId() == newaction['id'] \
                        and action.getCategory() in (newaction['category'], 'folder'):
                    del_idxs.append(idx)
                idx += 1
            actionsTool.deleteActions(del_idxs)

            #Add the action
            actionsTool.addAction(newaction['id'],
                name=newaction['name'],
                action=newaction['action'],
                condition=newaction['condition'],
                permission=newaction['permission'],
                category=newaction['category'],
                visible=1)

            out.append("Fixed '%s' action on actions tool." % newaction['name'])


def changePortalActionCategory(portal, out):
    """Change the category for the Plone Site type actions to 'object'"""
    EDIT_ACTIONS=('view','edit')
    OLD_CATEGORY='folder'
    NEW_CATEGORY='object'
    ttool = getToolByName(portal, 'portal_types', None)
    if ttool is not None:
        fti = getattr(ttool, 'Plone Site', None)
        if fti is not None:
            current_actions = fti._cloneActions()
            for action in current_actions:
                if action.getId() in EDIT_ACTIONS and action.category == OLD_CATEGORY:
                    action.category = 'object'
                    out.append("Changed category of Plone Site %s action to 'object'"%action.getId())
            fti._actions = current_actions


def addMethodAliasesForPloneSite(portal, out):
    """Add standard method aliases to Plone Site FTI"""
    aliases = {
                '(Default)'  : '(dynamic view)',
                'view'       : '(selected layout)',
                'index.html' : '(dynamic view)',
                'edit'       : 'folder_edit_form',
                'properties' : '',
                'sharing'    : 'folder_localrole_form',
                'gethtml'    : '',
                'mkdir'      : '',
              }
    ttool = getToolByName(portal, 'portal_types', None)
    if ttool is not None:
        fti = getattr(ttool, 'Plone Site', None)
        if fti is not None:
            cur_aliases = fti.getMethodAliases()
            if cur_aliases.get('view', None) != '(selected layout)':
                fti.setMethodAliases(aliases)
                out.append("Added method aliases to Plone Site FTI")

def updateParentMetaTypesNotToQuery(portal, out):
    """Add Large Plone Folder to the list of types not to query"""
    props = getattr(portal, 'portal_properties', None)
    if props is not None:
        ntp = getattr(props, 'navtree_properties', None)
        if ntp is not None:
            val = ntp.getProperty('parentMetaTypesNotToQuery',None)
            if val is None:
                ntp.manage_addProperty('parentMetaTypesNotToQuery',
                                            ['Large Plone Folder'], 'lines')
                out.append("Added missing 'parentMetaTypesNotToQuery' property to navtree_properties")
            elif 'Large Plone Folder' not in val:
                ntp.manage_changeProperties(parentMetaTypesNotToQuery=list(val)+['Large Plone Folder'])
                out.append("Added 'Large Plone Folder' to 'parentMetaTypesNotToQuery' in navtree_properties")


def fixCutActionPermission(portal,out):
    """Use more a reasonable permission for the cut action"""
    ACTIONS = (
        {'id'        : 'cut',
         'name'      : 'Cut',
         'action'    : 'python:"%s/object_cut"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)',
         'condition' : 'python:portal.portal_membership.checkPermission("Delete objects", object.aq_inner.getParentNode()) and portal.portal_membership.checkPermission("Copy or Move", object) and object is not portal and not (object.getParentNode() is portal and object.isDefaultPageInFolder())',
         'permission': DeleteObjects,
         'category'  : 'object_buttons',
        },
        )

    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        # update/add actions
        for newaction in ACTIONS:
            idx = 0
            for action in actionsTool.listActions():
                # if action exists, remove and re-add
                if action.getId() == newaction['id'] \
                        and action.getCategory() == newaction['category']:
                    actionsTool.deleteActions((idx,))
                    break
                idx += 1

            actionsTool.addAction(newaction['id'],
                name=newaction['name'],
                action=newaction['action'],
                condition=newaction['condition'],
                permission=newaction['permission'],
                category=newaction['category'],
                visible=1)

            out.append("Added '%s' contentmenu action to actions tool." % newaction['name'])


def fixExtEditAction(portal,out):
    """Make the external editor action appear in a reasonable way"""
    ACTIONS = (
            {'id'        : 'extedit',
             'name'      : 'Edit this file in an external application (Requires Zope ExternalEditor installed)',
             'action'    : 'string:$object_url/external_edit',
             'condition' : 'object/externalEditorEnabled',
             'permission': ModifyPortalContent,
             'category'  : 'document_actions'
            },)

    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        # update/add actions
        for newaction in ACTIONS:
            idx = 0
            for action in actionsTool.listActions():
                # if action exists, remove and re-add
                if action.getId() == newaction['id'] \
                        and action.getCategory() == newaction['category']:
                    actionsTool.deleteActions((idx,))
                    break
                idx += 1

            actionsTool.addAction(newaction['id'],
                name=newaction['name'],
                action=newaction['action'],
                condition=newaction['condition'],
                permission=newaction['permission'],
                category=newaction['category'],
                visible=1)

            out.append("Added '%s' action to actions tool." % newaction['name'])


def changeMemberdataExtEditor(portal, out):
    memberdata_tool = safeGetMemberDataTool(portal)
    if memberdata_tool is not None:
        safeEditProperty(memberdata_tool, 'ext_editor', 0, 'boolean')
        out.append("Turned off 'ext_editor' property on portal_memberdata by default.")


def fixWorkflowStateTitles(portal, out):
    """Fix titles for default workflow states"""
    wftool = getattr(portal, 'portal_workflow', None)
    wfs = ('plone_workflow','folder_workflow')
    state_titles = { 'private': 'Private',
                     'visible': 'Public Draft',
                     'pending': 'Pending',
                     'published': 'Published'
                    }
    for wfid in wfs:
        wf = getattr(wftool, wfid, None)
        wf_states = getattr(wf, 'states', None)
        if wf_states is not None:
            for state, title in state_titles.items():
                wf_state = getattr(wf.states, state, None)
                if wf_state is not None and wf_state.title != title:
                    wf_state.title = title
                    out.append("Updated workflow titles for state %s"%state)


def changeSiteActions(portal, out):
    """Remove text size actions, add accessibility and contact actions,
       move site setup to site_actions"""
    REMOVE_ACTIONS=('small_text','normal_text','large_text')
    REMOVE_CATEGORY='site_actions'
    ACTIONS=(    {'id': 'accessibility',
                  'name': 'Accessibility',
                  'action': 'string: ${portal_url}/accessibility-info',
                  'condition': '',
                  'permission': View,
                  'category': 'site_actions',
                  'visible': 1},
                 {'id': 'contact',
                  'name': 'Contact',
                  'action': 'string: ${portal_url}/contact-info',
                  'condition': '',
                  'permission': View,
                  'category': 'site_actions',
                  'visible': 1},
                 {'id': 'plone_setup',
                  'name': 'Site Setup',
                  'action': 'string: ${portal_url}/plone_control_panel',
                  'condition': '',
                  'permission': ManagePortal,
                  'category': 'site_actions',
                  'visible': 1}
            )
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        # First delete the text size toggle actions
        idx = 0
        del_idxs=[]
        for action in actionsTool.listActions():
            if action.getId() in REMOVE_ACTIONS \
                    and action.getCategory() == REMOVE_CATEGORY:
                del_idxs.append(idx)
            idx += 1
        actionsTool.deleteActions(del_idxs)

        # Now Remove and readd the contents action
        for newaction in ACTIONS:
            idx = 0
            del_idxs=[]
            for action in actionsTool.listActions():
                # if action exists, remove (including duplicates from any category)
                if action.getId() == newaction['id']:
                    del_idxs.append(idx)
                idx += 1
            actionsTool.deleteActions(del_idxs)

            #Add the action
            actionsTool.addAction(newaction['id'],
                name=newaction['name'],
                action=newaction['action'],
                condition=newaction['condition'],
                permission=newaction['permission'],
                category=newaction['category'],
                visible=1)

            out.append("Fixed '%s' action on actions tool." % newaction['name'])

def removePloneSetupActionFromPortalMembership(portal, out):
    """Remove plone_setup action from portal_membership"""
    REMOVE_ACTIONS=('plone_setup',)
    actionsTool = getToolByName(portal, 'portal_membership', None)
    if actionsTool is not None:
        # First delete the text size toggle actions
        idx = 0
        del_idxs=[]
        for action in actionsTool.listActions():
            if action.getId() in REMOVE_ACTIONS:
                del_idxs.append(idx)
                out.append("Removed action %s from portal_membership"%action.getId())
            idx += 1
        actionsTool.deleteActions(del_idxs)

def fixViewMethodAliases(portal, out):
    """The 'view' method alias should be (selected layout), not (default view),
    because you should be able to use /view to avoid any default-page being
    displayed. Fix all ATCT types and Plone Site.
    """
    types = ('Document', 'Event', 'Favorite', 'File', 'Folder', 'Image', 'Link', 'News Item', 'Topic', 'Plone Site')
    ttool = getToolByName(portal, 'portal_types', None)
    if ttool is not None:
        for typeName in types:
            fti = getattr(ttool, typeName, None)
            if fti is not None:
                aliases = fti.getMethodAliases().copy()
                if aliases.get('view', None) != '(selected layout)':
                    aliases['view'] = '(selected layout)'
                    fti.setMethodAliases(aliases)
                    out.append("Fixed 'view' method alias for %s FTI" % (typeName,))

def fixPortalEditAndSharingActions(portal, out):
    """The 'edit' and 'sharing' actions of the portal should use the method
    aliases /edit and /sharing.
    """
    ttool = getToolByName(portal, 'portal_types', None)
    if ttool is not None:
        fti = getattr(ttool, 'Plone Site', None)
        if fti is not None:
            for action in fti.listActions():
                if action.getId() == 'edit':
                    action.setActionExpression('string:${object_url}/edit')
                    out.append('Set portal root edit action to use /edit method alias')
                elif action.getId() == 'local_roles':
                    action.setActionExpression('string:${object_url}/sharing')
                    out.append('Set portal root sharing action to use /sharing method alias')
                    
def addCMFUidTools(portal, out):
    """Adds CMFUid tools to the plone instance
    
    CMFUid is an new CMF core product to handle uids the CMF way. CMF uids are
    different to AT uuids but can be used in parallel.
    """
    tools = (('Unique Id Annotation Tool', 'portal_uidannotation'),
             ('Unique Id Generator Tool', 'portal_uidgenerator'),
             ('Unique Id Handler Tool', 'portal_uidhandler')
            )
    added = []
    try:
        addCMFUidTool = portal.manage_addProduct['CMFUid'].manage_addTool
    except AttributeError:
        pass
    else:
        for tool, id in tools:
            try:
                addCMFUidTool(tool, None)
            except BadRequest:
                # already there
                pass
            else:
                tool = getattr(portal, id)
                tool.title = "CMF %s" % id
                added.append(id)
    if added:
        out.append('Added CMFUid tool(s) %s' % ', '.join(added))

def fixCSSMediaTypes(portal,out):
    """Fixes some css media types in the Resource Registry,
    like missing media type or wrong 'presentation' media type 
    """
    cssreg = getToolByName(portal, 'portal_css', None)
    stylesheet_ids = cssreg.getResourceIds()
    cssmediatypes = [
        ('member.css', 'screen'),
        ('RTL.css', 'screen'),
        ('presentation.css', 'projection'),
        ('ploneCustom.css', 'all'),
    ]
    changed=[]
    if cssreg is not None:
        for stylesheet,cssmediatype in cssmediatypes:
            if stylesheet in stylesheet_ids:
                cssresource=cssreg.getResource(stylesheet)
                cssresource.setMedia(cssmediatype)
                changed.append(stylesheet)
                out.append('Set media type for %s to %s' % (stylesheet,cssmediatype))
    if changed:
        out.append('Corrected CSS media types')

def addWFStateFilteringToNavTree(portal,out):
    """ Adds enable_wf_state_filtering and wf_states_to_show properties to the
        navtree_properties
    """
    props = getToolByName(portal, 'portal_properties', None)
    propSheet = getattr(props, 'navtree_properties', None)
    if propSheet is not None:
        if not propSheet.hasProperty('enable_wf_state_filtering'):
            propSheet.manage_addProperty('enable_wf_state_filtering', 0, 'boolean')
        out.append("Added 'enable_wf_state_filtering' property to navtree_properties.")
        if not propSheet.hasProperty('wf_states_to_show'):
            propSheet.manage_addProperty('wf_states_to_show', [], 'lines')
        out.append("Added 'wf_states_to_show' property to navtree_properties.")

def addIconForNavigationSettingsConfiglet(portal, out):
    """Adds an icon for the navigation settings configlet. """
    iconsTool = getToolByName(portal, 'portal_actionicons', None)
    if iconsTool is not None:
        for icon in iconsTool.listActionIcons():
            if icon.getActionId() == 'NavigationSettings':
                break # We already have the icon
        else:
            iconsTool.addActionIcon(
                category='controlpanel',
                action_id='NavigationSettings',
                icon_expr='navigation_icon.gif',
                title='Navigation Settings',
                )
        out.append("Added 'navigation' icon to actionicons tool.")

def addSearchAndNavigationConfiglets(portal, out):
    """Add the configlets for the search and navigation settings"""
    controlPanel = getToolByName(portal, 'portal_controlpanel', None)
    if controlPanel is not None:
        haveSearch = False
        haveNavigation = False
        for configlet in controlPanel.listActions():
            if configlet.getId() == 'SearchSettings':
                haveSearch = True
            if configlet.getId() == 'NavigationSettings':
                haveNavigation = True
        if not haveSearch:
            controlPanel.registerConfiglet(id         = 'SearchSettings',
                                           appId      = 'Plone',
                                           name       = 'Search Settings',
                                           action     = 'string:${portal_url}/prefs_search_form',
                                           category   = 'Plone',
                                           permission = ManagePortal,)
            out.append("Added search settings to the control panel")
        if not haveNavigation:
            controlPanel.registerConfiglet(id         = 'NavigationSettings',
                                           appId      = 'Plone',
                                           name       = 'Navigation Settings',
                                           action     = 'string:${portal_url}/prefs_navigation_form',
                                           category   = 'Plone',
                                           permission = ManagePortal,)
            out.append("Added navigation settings to the control panel")

def addFormSubmitHelpersJS(portal, out):
    """Add formsubmithelpers.js to ResourceRegistries.
    """
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    if jsreg is not None:
        if not 'formsubmithelpers.js' in jsreg.getResourceIds():
            jsreg.registerScript('formsubmithelpers.js')
            out.append('Registered formsubmithelpers.js')

def setupAllowSendtoPermission(portal, out):
    """Setup and configure new Allow Sendto permission
    """
    portal.manage_permission(AllowSendto,
                             ('Anonymous', 'Manager', 'Member',),
                             acquire=1)
    atool = getToolByName(portal, 'portal_actions', None)
    if atool is None:
        return
    actions = atool._cloneActions()
    for action in actions:
        if action.getId() == "sendto":
            action.permissions = (AllowSendto,)
    atool._actions = actions
    out.append("Changed sendto action permission to Allow Sendto")        

def readdVisibleIdsMemberProperty(portal, out):
    """Re-Adds member config for editable short names."""
    mpropTool = getToolByName(portal, 'portal_memberdata', None)
    if mpropTool is not None:
        if not mpropTool.hasProperty('visible_ids'):
            mpropTool.manage_addProperty('visible_ids', 0, 'boolean')
        out.append("Added 'visible_ids' property to portal_memberdata.")
        out.append("Added 'visible_ids' property to portal_memberdata.")


def addCMFTypesToSearchBlackList(portal, out):
    """Adds CMF types to types_not_searched site property."""
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
    MORE_TYPES_NOT_SEARCHED = ['CMF Document',
                               'CMF Event',
                               'CMF Favorite',
                               'CMF File',
                               'CMF Folder',
                               'CMF Image',
                               'CMF Large Plone Folder',
                               'CMF Link',
                               'CMF News Item',
                               'CMF Topic']

    propTool = getToolByName(portal, 'portal_properties', None)
    propSheet = getattr(propTool, 'site_properties', None)
    if propSheet is not None:
        old_val = propSheet.getProperty('types_not_searched', None)
        if old_val is None:
            propSheet.manage_addProperty('types_not_searched',
                                             BASE_TYPES_NOT_SEARCHED +
                                             MORE_TYPES_NOT_SEARCHED,
                                             'lines')
            out.append("Added 'types_not_searched' property to site_properties.")
        elif 'CMF Document' not in old_val:
            propSheet.manage_changeProperties(types_not_searched=list(old_val) +
                                              MORE_TYPES_NOT_SEARCHED)
            out.append("Added CMF types to 'types_not_searched' property.")

def convertDefaultPageTypesToWhitelist(portal, out):
    """Adds non_default_page_types site property."""
    # Types which are not selectable as a default_page
    DEFAULT_PAGE_TYPES = ('Document', 'Event', 'Link', 'News Item', 'Topic')

    propTool = getToolByName(portal, 'portal_properties', None)
    propSheet = getattr(propTool, 'site_properties', None)
    if propSheet is not None:
        if propSheet.hasProperty('non_default_page_types'):
            propSheet.manage_delProperties(['non_default_page_types'])
            out.append("Removed 'non_default_page_types' property to site_properties.")
        if not propSheet.hasProperty('default_page_types'):
            propSheet.manage_addProperty('default_page_types',
                                         DEFAULT_PAGE_TYPES, 'lines')
            out.append("Added 'default_page_types' property to site_properties.")
