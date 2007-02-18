from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import getUtility

from zope.app.component.interfaces import ISite
from zope.component.globalregistry import base
from zope.component.persistentregistry import PersistentComponents

from Acquisition import aq_base

from Products.ATContentTypes.migration.v1_2 import upgradeATCTTool
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionCategory
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.DirectoryView import createDirectoryView
from Products.CMFPlone.interfaces import IControlPanel
from Products.CMFPlone.interfaces import IInterfaceTool
from Products.CMFPlone.interfaces import IMigrationTool
from Products.CMFPlone.interfaces import ITranslationServiceTool
from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct
from Products.Five.component import enableSite
from Products.Five.component.interfaces import IObjectManagerSite

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY as CONTEXT_PORTLETS

from plone.app.portlets.utils import convert_legacy_portlets

def three0_alpha1(portal):
    """2.5.x -> 3.0-alpha1
    """
    out = []

    # Make the portal a Zope3 site
    enableZope3Site(portal, out)

    # Migrate old ActionInformation to Actions and move them to the actions tool
    migrateOldActions(portal, out)

    # Add new css files to RR
    addNewCSSFiles(portal, out)

    # Add new properties for default- and forbidden content types
    addDefaultAndForbiddenContentTypesProperties(portal, out)
    addTypesConfiglet(portal, out)

    # Actions should gain a i18n_domain now, so their title and description are
    # returned as Messages
    updateActionsI18NDomain(portal, out)

    # Type information should gain a i18n_domain now, so their title and
    # description are returned as Messages
    updateFTII18NDomain(portal, out)

    # The ATCT tool has lost all type migration functionality and quite some
    # metadata and index information stored on it needs to be updated.
    upgradeATCTTool(portal, out)

    # Install CMFEditions and 
    installProduct('CMFEditions', portal, out)
    installProduct('CMFDiffTool', portal, out)

    # Migrate legacy portlets
    convertLegacyPortlets(portal, out)

    # Add icon for calendar settings configlet
    addIconForCalendarSettingsConfiglet(portal, out)

    # Install the calendar settings control panel
    addCalendarConfiglet(portal, out)

    return out

def alpha1_alpha2(portal):
    """ 3.0-alpha1 -> 3.0-alpha2
    """
    out = []

    # Update search and mailhost control panels to new formlib based ones
    updateSearchAndMailHostConfiglet(portal, out)

    # remove generated.css from ResourceRegistries
    removeGeneratedCSS(portal, out)

    # add form_tabbing.js
    addFormTabbingJS(portal, out)

    # register some tools as utilities
    registerToolsAsUtilities(portal, out)

    # install the kss bits
    installKss(portal, out)

    # install plone.app.redirector
    installRedirectorUtility(portal, out)

    # Add action for plone.app.contentrules
    addContentRulesAction(portal, out)

    # Add reader and editor roles
    addReaderAndEditorRoles(portal, out)

    # Change folder_localrole_form to @@sharing
    migrateLocalroleForm(portal, out)

    # Reorder the user actions in a way that makes the getOrderedUserActions
    # script obsolete
    reorderUserActions(portal, out)

    # Update expression on RTL.css
    updateRtlCSSexpression(portal, out)

    return out


def alpha2_alpha3(portal):
    """ 3.0-alpha2 -> 3.0-alpha3
    """
    out = []

    # Add control panel actions 
    addControlPanelActions(portal, out)

    return out


def enableZope3Site(portal, out):
    if not ISite.providedBy(portal):
        enableSite(portal, iface=IObjectManagerSite)

        components = PersistentComponents()
        components.__bases__ = (base,)
        portal.setSiteManager(components)

        out.append('Made the portal a Zope3 site.')


def migrateOldActions(portal, out):
    special_providers = ['portal_controlpanel',
                         'portal_types',
                         'portal_workflow']
    # We don't need to operate on the providers that are still valid and
    # should ignore the control panel as well
    providers = [obj for obj in portal.objectValues()
                     if hasattr(obj, '_actions') and
                     obj.getId() not in special_providers]
    non_empty_providers = [p for p in providers if len(p._actions) > 0]
    for provider in non_empty_providers:
        for action in provider._actions:
            category = action.category
            # check if the category already exists, otherwise create it
            new_category = getattr(aq_base(portal.portal_actions), category, None)
            if new_category is None:
                portal.portal_actions._setObject(category, ActionCategory(id=category))
                new_category = portal.portal_actions[category]

            # Special handling for Expressions
            url_expr = ''
            if action.action:
                url_expr = action.action.text
            available_expr = ''
            if action.condition:
                available_expr = action.condition.text

            new_action = Action(action.id,
                title=action.title,
                description=action.description,
                url_expr=url_expr,
                available_expr=available_expr,
                permissions=action.permissions,
                visible = action.visible)
                
            # Only add an action if there isn't one with that name already
            if getattr(new_category, action.id, None) is None:
                new_category._setObject(action.id, new_action)

        # Remove old actions from migrated providers
        provider._actions = ()
    out.append('Migrated old actions to new actions stored in portal_actions.')

def addNewCSSFiles(portal, out):
    # add new css files to the portal_css registries
    cssreg = getToolByName(portal, 'portal_css', None)
    stylesheet_ids = cssreg.getResourceIds()
    if 'navtree.css' not in stylesheet_ids:
        cssreg.registerStylesheet('navtree.css', media='screen')
        cssreg.moveResourceAfter('navtree.css', 'textLarge.css')
        out.append("Added navtree.css to the registry")
    if 'invisibles.css' not in stylesheet_ids:
        cssreg.registerStylesheet('invisibles.css', media='screen')
        cssreg.moveResourceAfter('invisibles.css', 'navtree.css')
        out.append("Added invisibles.css to the registry")
    if 'forms.css' not in stylesheet_ids:
        cssreg.registerStylesheet('forms.css', media='screen')
        cssreg.moveResourceAfter('forms.css', 'invisibles.css')
        out.append("Added forms.css to the registry")

def addDefaultAndForbiddenContentTypesProperties(portal, out):
    """Adds sitewide config for default and forbidden content types for AT textfields."""
    propTool = getToolByName(portal, 'portal_properties', None)
    if propTool is not None:
        propSheet = getattr(aq_base(propTool), 'site_properties', None)
        if propSheet is not None:
            if not propSheet.hasProperty('default_contenttype'):
                propSheet.manage_addProperty('default_contenttype', 'text/html', 'string')
            out.append("Added 'default_contenttype' property to site_properties.")
            if not propSheet.hasProperty('forbidden_contenttypes'):
                propSheet.manage_addProperty('forbidden_contenttypes', [], 'lines')
                propSheet.forbidden_contenttypes = (
                    'text/structured', 
                    'text/x-rst', 
                    'text/plain-pre', 
                    'text/x-python', 
                    'text/x-web-textile')
            out.append("Added 'forbidden_contenttypes' property to site_properties.")

def addTypesConfiglet(portal, out):
    """Add the types configlet."""
    controlPanel = getToolByName(portal, 'portal_controlpanel', None)
    if controlPanel is not None:
        gotTypes = False
        for configlet in controlPanel.listActions():
            if configlet.getId() == 'TypesSettings':
                gotTypes = True
        if not gotTypes:
            controlPanel.registerConfiglet(
                id         = 'TypesSettings',
                appId      = 'Plone',
                name       = 'Types Settings',
                action     = 'string:${portal_url}/@@types-controlpanel.html',
                category   = 'Plone',
                permission = ManagePortal,
            )
            out.append("Added Types Settings to the control panel")

def updateActionsI18NDomain(portal, out):
    actions = portal.portal_actions.listActions()
    domainless_actions = [a for a in actions if not a.i18n_domain]
    for action in domainless_actions:
        action.i18n_domain = 'plone'
    out.append('Updated actions i18n domain attribute.')

def updateFTII18NDomain(portal, out):
    types = portal.portal_types.listTypeInfo()
    domainless_types = [fti for fti in types if not fti.i18n_domain]
    for fti in domainless_types:
        fti.i18n_domain = 'plone'
    out.append('Updated type informations i18n domain attribute.')

def convertLegacyPortlets(portal, out):
    """Convert portlets defined in left_slots and right_slots at the portal
    root to use plone.portlets. Also block portlets in the Members folder.
    
    Note - there may be other portlets defined elsewhere. These will require
    manual migration from the @@manage-portlets view. This is to avoid a 
    full walk of the portal (i.e. waking up every single object) looking for
    potential left_slots/right_slots! 
    """
    convert_legacy_portlets(portal)
    out.append('Converted legacy portlets at the portal root')
    out.append('NOTE: You may need to convert other portlets manually.')
    out.append(' - to do so, click "manage portlets" in the relevant folder.')
    
    members = getattr(portal, 'Members', None)
    if members is not None:
        membersRightSlots = getattr(aq_base(members), 'right_slots', None)
        if membersRightSlots == []:
            rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
            portletAssignments = getMultiAdapter((members, rightColumn,), ILocalPortletAssignmentManager)
            portletAssignments.setBlacklistStatus(CONTEXT_PORTLETS, True)
            out.append('Blacklisted contextual portlets in the Members folder')

def installProduct(product, portal, out):
    """Quickinstalls a product if it is not installed yet."""
    if product in portal.Control_Panel.Products.objectIds():
        installOrReinstallProduct(portal, product, out)

def addIconForCalendarSettingsConfiglet(portal, out):
    """Adds an icon for the calendar settings configlet. """
    iconsTool = getToolByName(portal, 'portal_actionicons', None)
    if iconsTool is not None:
        for icon in iconsTool.listActionIcons():
            if icon.getActionId() == 'CalendarSettings':
                break # We already have the icon
        else:
            iconsTool.addActionIcon(
                category='controlpanel',
                action_id='CalendarSettings',
                icon_expr='event_icon.gif',
                title='Calendar Settings',
                )
        out.append("Added 'calendar' icon to actionicons tool.")

def addCalendarConfiglet(portal, out):
    """Add the configlet for the calendar settings"""
    controlPanel = getToolByName(portal, 'portal_controlpanel', None)
    if controlPanel is not None:
        haveCalendar = False
        for configlet in controlPanel.listActions():
            if configlet.getId() == 'CalendarSettings':
                haveCalendar = True
        if not haveCalendar:
            controlPanel.registerConfiglet(id         = 'CalendarSettings',
                                           appId      = 'Plone',
                                           name       = 'Calendar Settings',
                                           action     = 'string:${portal_url}/@@calendar-controlpanel.html',
                                           category   = 'Plone',
                                           permission = ManagePortal,)
            out.append("Added calendar settings to the control panel")

def updateSearchAndMailHostConfiglet(portal, out):
    """Use new configlets for the search and mailhost settings"""
    controlPanel = getToolByName(portal, 'portal_controlpanel', None)
    if controlPanel is not None:
        search = controlPanel.getActionObject('Plone/SearchSettings')
        mail = controlPanel.getActionObject('Plone/MailHost')

        if search is not None:
            search.action = Expression('string:${portal_url}/@@search-controlpanel.html')
        if mail is not None:
            mail.action = Expression('string:${portal_url}/@@mail-controlpanel.html')

def removeGeneratedCSS(portal, out):
    # remove generated.css from the portal_css registries
    cssreg = getToolByName(portal, 'portal_css', None)
    stylesheet_ids = cssreg.getResourceIds()
    if 'generated.css' in stylesheet_ids:
        cssreg.unregisterResource('generated.css')
        out.append("Removed generated.css from the registry")

def addFormTabbingJS(portal, out):
    """Add form_tabbing.js to ResourceRegistries.
    """
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    script = 'form_tabbing.js'
    if jsreg is not None:
        script_ids = jsreg.getResourceIds()
        # Failsafe: first make sure the stylesheet doesn't exist in the list
        if script not in script_ids:
            jsreg.registerScript(script)
            try:
                jsreg.moveResourceAfter(script, 'collapsiblesections.js')
            except ValueError:
                # put it at the bottom of the stack
                jsreg.moveResourceToBottom(script)
            out.append("Added " + script + " to portal_javascipt")

def registerToolsAsUtilities(portal, out):
    sm = getSiteManager(portal)
    registration = ((portal.portal_controlpanel, IControlPanel),
                    (portal.portal_interface, IInterfaceTool),
                    (portal.portal_migration, IMigrationTool),
                    (portal.translation_service, ITranslationServiceTool),
                   )
    for reg in registration:
        if sm.queryUtility(reg[1]) is None:
            sm.registerUtility(reg[0], reg[1])

    out.append("Registered controlpanel, interface, migration and translation "
               "service tools as utilities.")

def installRedirectorUtility(portal, out):
    from plone.app.redirector.interfaces import IRedirectionStorage
    from plone.app.redirector.storage import RedirectionStorage
    
    sm = getSiteManager(portal)
    if sm.queryUtility(IRedirectionStorage) is None:
        sm.registerUtility(RedirectionStorage(), IRedirectionStorage)

    out.append("Registered redirector utility")

def addContentRulesAction(portal, out):
    portal_actions = getToolByName(portal, 'portal_actions', None)
    if portal_actions is not None:
        object_buttons = getattr(portal_actions, 'object_buttons', None)
        if object_buttons is not None:
            if 'contentrules' not in object_buttons.objectIds():
                new_action = Action('contentrules',
                                    title='Rules',
                                    description='',
                                    url_expr='string:${plone_context_state/canonical_object_url}/@@manage-content-rules',
                                    available_expr="python:plone_context_state.canonical_object()['@@plone_interface_info'].provides('plone.contentrules.engine.interfaces.IRuleContainer')",
                                    permissions='Manage portal',
                                    visible=True)
                object_buttons._setObject('contentrules', new_action)
                out.append("Added content rules action to object_buttons")

def addReaderAndEditorRoles(portal, out):
    if 'Reader' not in portal.valid_roles():
        portal._addRole('Reader')
    if 'Editor' not in portal.valid_roles():
        portal._addRole('Editor')
    if 'Reader' not in portal.acl_users.portal_role_manager.listRoleIds():
        portal.acl_users.portal_role_manager.addRole('Reader')
    if 'Editor' not in portal.acl_users.portal_role_manager.listRoleIds():
        portal.acl_users.portal_role_manager.addRole('Editor')
    
    viewRoles = [r['name'] for r in portal.rolesOfPermission('View') if r['selected']]
    modifyRoles = [r['name'] for r in portal.rolesOfPermission('Modify portal content') if r['selected']]
    
    if 'Reader' not in viewRoles:
        viewRoles.append('Reader')
        portal.manage_permission('View', viewRoles, True)
        
    if 'Editor' not in modifyRoles:
        modifyRoles.append('Editor')
        portal.manage_permission('Modify portal content', modifyRoles, True)

    out.append('Added reader and editor roles')

def migrateLocalroleForm(portal, out):
    portal_types = getToolByName(portal, 'portal_types', None)
    if portal_types is not None:
        for fti in portal_types.objectValues():
            
            aliases = fti.getMethodAliases()
            new_aliases = aliases.copy()
            for k, v in aliases.items():
                if 'folder_localrole_form' in v:
                    new_aliases[k] = v.replace('folder_localrole_form', '@@sharing')
            fti.setMethodAliases(new_aliases)
            
            for a in fti.listActions():
                expr = a.getActionExpression()
                if 'folder_localrole_form' in expr:
                    a.setActionExpression(expr.replace('folder_localrole_form', '@@sharing'))
    out.append('Ensured references to folder_localrole_form point to @@sharing now')

def reorderUserActions(portal, out):
    portal_actions = getToolByName(portal, 'portal_actions', None)
    if portal_actions is not None:
        user_category = getattr(portal_actions, 'user', None)
        if user_category is not None:        
            new_actions = ['login', 'join', 'mystuff', 'preferences', 'undo', 'logout']
            new_actions.reverse()
            for action in new_actions:
                if action in user_category.objectIds():
                    user_category.moveObjectsToTop([action])

def updateRtlCSSexpression(portal, out):
    # update expression on rtl css file
    cssreg = getToolByName(portal, 'portal_css', None)
    if cssreg is not None:
        stylesheet_ids = cssreg.getResourceIds()
        if 'RTL.css' in stylesheet_ids:
            rtl = cssreg.getResource('RTL.css')
            rtl.setExpression("python:portal.restrictedTraverse('@@plone_portal_state').is_rtl()")
            out.append("Updated RTL.css expression.")

def addControlPanelActions(portal, out):
    cpanel = getToolByName(portal,'portal_controlpanel')
    if not getattr(cpanel, 'Maintenance', None):
        new_action = Action('Maintenance',
                            title='Maintenance',
                            description='',
                            category="Plone",
                            url_expr='string:${portal_url}/@@Maintenance-controlpanel.pt',
                            available_expr='',
                            permissions='Manage portal',
                            visible=True)
        cpanel._setObject('Maintenance', new_action)
        out.append("Added Maintenance action to plone_controlpanel")


# --
# KSS registration
# --

class installKss(object):

    js_unregister = []

    js_all = [
        ('++resource++MochiKit.js', 'none', False),
        ('++resource++prototype.js', 'safe', True),
        ('++resource++effects.js', 'safe', True),
        ('++resource++kukit.js', 'none', True),
    ]

    css_all = [
        'ploneKss.css',
    ]

    kss_all = [
        'plone.kss',
        'at.kss',
    ]

    def __init__(self, portal, out):
        self.portal = portal
        self.out = out
        self.installKss()

    @staticmethod
    def _old_res(tool, id):
        return tool.getResourcesDict().get(id, None)
     
    def install_resources(self):
        portal, out = self.portal, self.out
        jstool = getToolByName(portal, 'portal_javascripts')
        for id in self.js_unregister:
            if self._old_res(jstool, id):
                jstool.unregisterResource(id)
                out.append("Unregistered old %s" % (id, ))
        for id, compression, enabled in self.js_all:
            if not self._old_res(jstool, id):
                jstool.registerScript(
                    id = id,
                    enabled = enabled,
                    cookable = True,
                    compression = compression,
                    )
        csstool = getToolByName(portal, 'portal_css')
        for css in self.css_all:
            if not self._old_res(csstool, css):
                csstool.manage_addStylesheet(
                    id = css,
                    rel = 'stylesheet',
                    rendering = 'link',
                    enabled = True,
                    cookable = True,
                    )
        # kss stylesheets
        for kss in self.kss_all:
            if not self._old_res(csstool, kss):
                csstool.manage_addStylesheet(id=kss,
                    rel='k-stylesheet',
                    rendering = 'link',
                    enabled=True,
                    cookable=False,
                    )
        out.append("Registered kss resources")

    def install_mimetype(self):
        portal, out = self.portal, self.out
        mt = getToolByName(portal, 'mimetypes_registry')
        mt.manage_addMimeType('KSS (Azax) StyleSheet', ('text/kss', ), ('kss', ), 'text.png',
                               binary=0, globs=('*.kss', ))
        out.append("Registered kss mimetype")

    def install_skins(self):
        portal, out = self.portal, self.out
        st = getToolByName(portal, 'portal_skins')
        skins = ['Plone Default', 'Plone Tableless']
        if not hasattr(aq_base(st), 'plone_kss'):
            createDirectoryView(st, 'CMFPlone/skins/plone_kss')
        if not hasattr(aq_base(st), 'archetypes_kss'):
            createDirectoryView(st, 'Archetypes/skins/archetypes_kss')
        selections = st._getSelections()
        for s in skins:
            if not selections.has_key(s):
               continue
            path = st.getSkinPath(s)
            path = [p.strip() for p in  path.split(',')]
            path_changed = False
            if not 'plone_kss' in path:
                path.append('plone_kss')
                path_changed = True
            if not 'archetypes_kss' in path:
                path.append('archetypes_kss')
                path_changed = True
            if path_changed:
                st.addSkinSelection(s, ','.join(path))
                out.append('Added missing skins to %s' % s)

    def installKss(self):
        out = self.out
        self.install_mimetype() 
        self.install_resources() 
        self.install_skins() 
        out.append("Succesfully migrated portal to KSS")

