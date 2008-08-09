import os

from five.localsitemanager import make_objectmanager_site
from five.localsitemanager.registry import FiveVerifyingAdapterLookup
from zope.app.component.interfaces import ISite
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import getUtility

from Acquisition import aq_base
from Globals import package_home

from Products.StandardCacheManagers import RAMCacheManager

from Products.Archetypes.interfaces import IArchetypeTool
from Products.Archetypes.interfaces import IReferenceCatalog
from Products.Archetypes.interfaces import IUIDCatalog
from Products.ATContentTypes.interface import IATCTTool
from Products.ATContentTypes.migration.v1_2 import upgradeATCTTool
from Products.CMFActionIcons.interfaces import IActionIconsTool
from Products.CMFCalendar.interfaces import ICalendarTool
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionCategory
from Products.CMFCore.Expression import Expression
from Products.CMFCore.interfaces import IActionsTool
from Products.CMFCore.interfaces import ICachingPolicyManager
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.interfaces import IContentTypeRegistry
from Products.CMFCore.interfaces import IDiscussionTool
from Products.CMFCore.interfaces import IMemberDataTool
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.interfaces import IMetadataTool
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.interfaces import IRegistrationTool
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.interfaces import ISkinsTool
from Products.CMFCore.interfaces import ISyndicationTool
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.interfaces import IUndoTool
from Products.CMFCore.interfaces import IURLTool
from Products.CMFCore.interfaces import IConfigurableWorkflowTool
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.DirectoryView import createDirectoryView
from Products.CMFDiffTool.interfaces import IDiffTool
from Products.CMFEditions.interfaces import IArchivistTool
from Products.CMFEditions.interfaces import IPortalModifierTool
from Products.CMFEditions.interfaces import IPurgePolicyTool
from Products.CMFEditions.interfaces.IRepository import IRepositoryTool
from Products.CMFEditions.interfaces import IStorageTool
from Products.CMFFormController.interfaces import IFormControllerTool
from Products.CMFPlone import cmfplone_globals
from Products.CMFPlone.interfaces import IControlPanel
from Products.CMFPlone.interfaces import IFactoryTool
from Products.CMFPlone.interfaces import IInterfaceTool
from Products.CMFPlone.interfaces import IMigrationTool
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces import IPloneTool
from Products.CMFPlone.interfaces import ITranslationServiceTool
from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct
from Products.CMFPlone.migrations.migration_util import loadMigrationProfile
from Products.CMFQuickInstallerTool.interfaces import IQuickInstallerTool
from Products.CMFUid.interfaces import IUniqueIdAnnotationManagement
from Products.CMFUid.interfaces import IUniqueIdGenerator
from Products.CMFUid.interfaces import IUniqueIdHandler
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.exportimport import WorkflowDefinitionConfigurator, _initDCWorkflow
from Products.GenericSetup.interfaces import ISetupTool
from Products.MailHost.interfaces import IMailHost
from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool
from Products.PloneLanguageTool.interfaces import ILanguageTool
from Products.PlonePAS.interfaces.group import IGroupTool
from Products.PlonePAS.interfaces.group import IGroupDataTool
from Products.PortalTransforms.interfaces import IPortalTransformsTool
from Products.ResourceRegistries.interfaces import ICSSRegistry
from Products.ResourceRegistries.interfaces import IJSRegistry

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

    # register some tools as utilities
    registerToolsAsUtilities(portal, out)

    # Updates the available import steps, so the componentregistry step is
    # available for add-on product installation
    updateImportStepsFromBaseProfile(portal, out)

    # Migrate old ActionInformation to Actions and move them to the actions tool
    migrateOldActions(portal, out)

    # Add new css files to RR
    addNewCSSFiles(portal, out)

    # Add new properties for default- and forbidden content types
    addDefaultAndForbiddenContentTypesProperties(portal, out)
    addMarkupConfiglet(portal, out)
    addIconForMarkupConfiglet(portal, out)

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
    installProduct('CMFDiffTool', portal, out, hidden=True)
    installProduct('CMFEditions', portal, out, hidden=True)

    # Migrate legacy portlets
    addPortletManagers(portal, out)

    # Migrate legacy portlets
    convertLegacyPortlets(portal, out)

    # Add icon for calendar settings configlet
    addIconForCalendarSettingsConfiglet(portal, out)

    # Install the calendar settings control panel
    addCalendarConfiglet(portal, out)

    # Deal with the tableless skin disappearing
    removeTablelessSkin(portal, out)

    return out

def alpha1_alpha2(portal):
    """ 3.0-alpha1 -> 3.0-alpha2
    """
    out = []

    # register some tools as utilities
    enableZope3Site(portal, out)
    registerToolsAsUtilities(portal, out)

    # Update search and mailhost control panels to new formlib based ones
    updateSearchAndMailHostConfiglet(portal, out)

    # remove generated.css from ResourceRegistries
    removeGeneratedCSS(portal, out)

    # add form_tabbing.js
    addFormTabbingJS(portal, out)

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


def alpha2_beta1(portal):
    """ 3.0-alpha2 -> 3.0-beta1
    """
    out = []

    # register some tools as utilities
    enableZope3Site(portal, out)
    registerToolsAsUtilities(portal, out)

    # Add control panel action 
    addMaintenanceConfiglet(portal, out)
    
    # Add action icon
    addIconForMaintenanceConfiglet(portal, out)

    # Add number_of_days_to_keep property
    addMaintenanceProperty(portal, out)

    installS5(portal, out)
    
    addTableContents(portal, out)

    # add input-label.js
    addFormInputLabelJS(portal, out)
    
    #modify member security settings to match new default policies
    updateMemberSecurity(portal, out)

    updatePASPlugins(portal, out)
    
    # Update control panel actions
    updateSkinsAndSiteConfiglet(portal, out)

    # Rename some control panel titles
    updateConfigletTitles(portal, out)

    # Add icon for filter and security configlets
    addIconsForFilterAndSecurityConfiglets(portal, out)

    # add content rules configlet
    installContentRulesUtility(portal, out)
    addContentRulesConfiglet(portal, out)
    addIconForContentRulesConfiglet(portal, out)

    # Install the filter and security control panels
    addFilterAndSecurityConfiglets(portal, out)

    # Add the sitemap enabled property
    addSitemapProperty(portal, out)

    # Use the unpacked kukit-src.js and pack it ourself
    updateKukitJS(portal, out)

    # Add a RAMCache for ResourceRegistries
    addCacheForResourceRegistry(portal, out)

    # Compress cssQuery with full-encode like it's supposed to.
    updateCssQueryJS(portal, out)

    # Remove very old javascript
    removeHideAddItemsJS(portal, out)

    # Add webstats.js for Google Analytics
    addWebstatsJSFile(portal,out)
    
    # Add webstats_js property to site properties
    addWebstatsJSProperty(portal,out)

    # Add the object_provides catalog index
    addObjectProvidesIndex(portal, out)

    # Remove the mystuff user action
    removeMyStuffAction(portal, out)

    # Add external_links_open_new_window property to site properties
    addExternalLinksOpenNewWindowProperty(portal, out)

    # Add the types configlet
    addTypesConfiglet(portal, out)
    addIconForTypesConfiglet(portal, out)
    
    # Add workflows that people may be missing
    addMissingWorkflows(portal, out)

    # Add many_groups property to site properties
    addManyGroupsProperty(portal, out)

    # Replace obsolete PlonePAS version of plone tool
    restorePloneTool(portal, out)

    # install plone.app.i18n
    installI18NUtilities(portal, out)

    # Install PloneLanguageTool
    installProduct('PloneLanguageTool', portal, out, hidden=True)

    # Add email_charset property
    addEmailCharsetProperty(portal, out)

    return out

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


def enableZope3Site(portal, out):
    if not ISite.providedBy(portal):
        make_objectmanager_site(portal)
        out.append('Made the portal a Zope3 site.')
    else:
        sm = portal.getSiteManager()
        if sm.utilities.LookupClass  != FiveVerifyingAdapterLookup:
            sm.utilities.LookupClass = FiveVerifyingAdapterLookup
            sm.utilities._createLookup()
            sm.utilities.__parent__ = aq_base(sm)
            sm.__parent__ = aq_base(portal)


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
            if getattr(aq_base(new_category), action.id, None) is None:
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
        cssreg.moveResourceAfter('navtree.css', 'deprecated.css')
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
                    'text/x-web-markdown',
                    'text/x-web-textile',
                    'text/x-web-intelligent')
            out.append("Added 'forbidden_contenttypes' property to site_properties.")


def addMarkupConfiglet(portal, out):
    """Add the markup configlet."""
    controlPanel = getToolByName(portal, 'portal_controlpanel', None)
    if controlPanel is not None:
        gotMarkup = False
        for configlet in controlPanel.listActions():
            if configlet.getId() == 'MarkupSettings':
                gotMarkup = True
        if not gotMarkup:
            controlPanel.registerConfiglet(
                id         = 'MarkupSettings',
                appId      = 'Plone',
                name       = 'Markup',
                action     = 'string:${portal_url}/@@markup-controlpanel',
                category   = 'Plone',
                permission = ManagePortal,
            )
            out.append("Added Markup Settings to the control panel")


def addIconForMarkupConfiglet(portal, out):
    """Adds an icon for the markup settings configlet. """
    iconsTool = getToolByName(portal, 'portal_actionicons', None)
    if iconsTool is not None:
        for icon in iconsTool.listActionIcons():
            if icon.getActionId() == 'MarkupSettings':
                break # We already have the icon
        else:
            iconsTool.addActionIcon(
                category='controlpanel',
                action_id='MarkupSettings',
                icon_expr='edit.gif',
                title='Markup',
                )
        out.append("Added markup configlet icon to actionicons tool.")     


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
                name       = 'Types',
                action     = 'string:${portal_url}/@@types-controlpanel',
                category   = 'Plone',
                permission = ManagePortal,
            )
            out.append("Added Types Settings to the control panel")


def addIconForTypesConfiglet(portal, out):
    """Adds an icon for the types settings configlet. """
    iconsTool = getToolByName(portal, 'portal_actionicons', None)
    if iconsTool is not None:
        for icon in iconsTool.listActionIcons():
            if icon.getActionId() == 'TypesSettings':
                break # We already have the icon
        else:
            iconsTool.addActionIcon(
                category='controlpanel',
                action_id='TypesSettings',
                icon_expr='document_icon.gif',
                title='Types',
                )
        out.append("Added types configlet icon to actionicons tool.")            


def _check_ascii(text):
    try:
        unicode(text, 'ascii')
    except UnicodeDecodeError:
        return False
    return True


def updateActionsI18NDomain(portal, out):
    actions = portal.portal_actions.listActions()
    domainless_actions = [a for a in actions if not a.i18n_domain]
    for action in domainless_actions:
        if _check_ascii(action.title) and _check_ascii(action.description):
            action.i18n_domain = 'plone'
    out.append('Updated actions i18n domain attribute.')


def updateFTII18NDomain(portal, out):
    types = portal.portal_types.listTypeInfo()
    domainless_types = [fti for fti in types if not fti.i18n_domain]
    for fti in domainless_types:
        if _check_ascii(fti.title) and _check_ascii(fti.description):
            fti.i18n_domain = 'plone'
    out.append('Updated type informations i18n domain attribute.')


def addPortletManagers(portal, out):
    """Add new portlets managers."""
    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:2.5-3.0a1',
            steps=['portlets'])
    

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


def installProduct(product, portal, out, hidden=False):
    """Quickinstalls a product if it is not installed yet."""
    if product in portal.Control_Panel.Products.objectIds():
        installOrReinstallProduct(portal, product, out, hidden=hidden)


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
                                           name       = 'Calendar',
                                           action     = 'string:${portal_url}/@@calendar-controlpanel',
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
            search.title = "Search"
            search.action = Expression('string:${portal_url}/@@search-controlpanel')
        if mail is not None:
            mail.title = "Mail"
            mail.action = Expression('string:${portal_url}/@@mail-controlpanel')


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


def addFormInputLabelJS(portal, out):
    """Add input-label.js to ResourceRegistries.
    """
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    script = 'input-label.js'
    if jsreg is not None:
        script_ids = jsreg.getResourceIds()
        # Failsafe: first make sure the stylesheet doesn't exist in the list
        if script not in script_ids:
            jsreg.registerScript(script)
            out.append("Added " + script + " to portal_javascipt")


registration = (('mimetypes_registry', IMimetypesRegistryTool),
                ('portal_transforms', IPortalTransformsTool),
                ('portal_atct', IATCTTool),
                ('portal_actionicons', IActionIconsTool),
                ('portal_discussion', IDiscussionTool),
                ('portal_metadata', IMetadataTool),
                ('portal_properties', IPropertiesTool),
                ('portal_syndication', ISyndicationTool),
                ('portal_undo', IUndoTool),
                ('portal_interface', IInterfaceTool),
                ('portal_migration', IMigrationTool),
                ('MailHost', IMailHost),
                ('portal_diff', IDiffTool),
                ('portal_uidannotation', IUniqueIdAnnotationManagement),
                ('portal_uidgenerator', IUniqueIdGenerator),
               )

invalid_regs = (ILanguageTool, IArchivistTool, IPortalModifierTool,
                IPurgePolicyTool, IRepositoryTool, IStorageTool,
                IFormControllerTool, IReferenceCatalog, IUIDCatalog,
                ICalendarTool, IActionsTool, ICatalogTool,
                IContentTypeRegistry, ISkinsTool, ITypesTool, IURLTool,
                IConfigurableWorkflowTool, IPloneTool, ICSSRegistry,
                IJSRegistry, IUniqueIdHandler, IFactoryTool, IMembershipTool,
                IGroupTool, IGroupDataTool, IMemberDataTool,
                ICachingPolicyManager, IRegistrationTool, IArchetypeTool,
                ITranslationServiceTool, IControlPanel, IQuickInstallerTool,
                ISetupTool,
               )

def registerToolsAsUtilities(portal, out):
    sm = getSiteManager(portal)

    portalregistration = ((portal, ISiteRoot),
                          (portal, IPloneSiteRoot),)

    for reg in portalregistration:
        if sm.queryUtility(reg[1]) is None:
            sm.registerUtility(aq_base(reg[0]), reg[1])

    for reg in registration:
        if sm.queryUtility(reg[1]) is None:
            if reg[0] in portal.keys():
                tool = aq_base(portal[reg[0]])
                sm.registerUtility(tool, reg[1])

    for reg in invalid_regs:
        if sm.queryUtility(reg) is not None:
            sm.unregisterUtility(provided=reg)

    out.append("Registered tools as utilities.")


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
        object_category = getattr(portal_actions, 'object', None)
        if object_category is not None:
            if 'contentrules' not in object_category.objectIds():
                new_action = Action('contentrules',
                                    title='Rules',
                                    description='',
                                    url_expr='string:${plone_context_state/canonical_object_url}/@@manage-content-rules',
                                    available_expr="python:plone_context_state.canonical_object().restrictedTraverse('@@plone_interface_info').provides('plone.contentrules.engine.interfaces.IRuleAssignable')",
                                    permissions='Content rules: Manage rules',
                                    visible=True)
                object_category._setObject('contentrules', new_action)
                out.append("Added content rules action to object category")


def installContentRulesUtility(portal, out):
    from plone.contentrules.engine.interfaces import IRuleStorage
    from plone.contentrules.engine.storage import RuleStorage
    
    sm = getSiteManager(portal)
    if sm.queryUtility(IRuleStorage) is None:
        sm.registerUtility(RuleStorage(), IRuleStorage)

    out.append("Registered content rules storage utility")


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
            if not hasattr(fti, '_aliases'):
                fti._aliases={}
            
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


def installS5(portal, out):
    portalTypes = getToolByName(portal, 'portal_types', None)
    if portalTypes is not None:
        document = portalTypes.restrictedTraverse('Document', None)
        if document:
            for action in document.listActions():
                if action.getId() == 's5_presentation':
                    break # We already have the action
            else:
                document.addAction('s5_presentation',
                    name='View as presentation',
                    action="string:${object/absolute_url}/document_s5_presentation",
                    condition='python:object.document_s5_alter(test=True)',
                    permission='View',
                    category='document_actions',
                    visible=1,
                    )
            out.append("Added 's5_presentation' action to actions tool.")

    iconsTool = getToolByName(portal, 'portal_actionicons', None)
    if iconsTool is not None:
        for icon in iconsTool.listActionIcons():
            if icon.getActionId() == 's5_presentation':
                break # We already have the icon
        else:
            iconsTool.addActionIcon(
                category='plone',
                action_id='s5_presentation',
                icon_expr='fullscreenexpand_icon.gif',
                title='View as presentation',
                )
        out.append("Added 's5_presentation' icon to actionicons tool.")


def addIconForMaintenanceConfiglet(portal, out):
    """Adds an icon for the maintenance settings configlet. """
    iconsTool = getToolByName(portal, 'portal_actionicons', None)
    if iconsTool is not None:
        for icon in iconsTool.listActionIcons():
            if icon.getActionId() == 'Maintenance':
                break # We already have the icon
        else:
            iconsTool.addActionIcon(
                category='controlpanel',
                action_id='Maintenance',
                icon_expr='maintenance_icon.gif',
                title='Maintenance',
                )
        out.append("Added 'maintenance' icon to actionicons tool.")


def addMaintenanceConfiglet(portal, out):
    """Add the configlet for the calendar settings"""
    controlPanel = getToolByName(portal, 'portal_controlpanel', None)
    if controlPanel is not None:
        havePanel = False
        for configlet in controlPanel.listActions():
            if configlet.getId() == 'Maintenance':
                havePanel = True
        if not havePanel:
            controlPanel.registerConfiglet(id         = 'Maintenance',
                                           appId      = 'Plone',
                                           name       = 'Maintenance',
                                           action     = 'string:${portal_url}/@@maintenance-controlpanel',
                                           category   = 'Plone',
                                           permission = ManagePortal,)
            out.append("Added 'Maintenance' to the control panel")


def addMaintenanceProperty(portal, out):
    """ adds a site property to portal_properties"""
    tool = getToolByName(portal, 'portal_properties', None)
    if tool is not None:
        sheet = getattr(tool, 'site_properties', None)
        if sheet is not None:
            if not sheet.hasProperty('number_of_days_to_keep'):
                sheet.manage_addProperty('number_of_days_to_keep', 7, 'int')
                out.append("Added 'number_of_days_to_keep' property to site properties")


def addWebstatsJSProperty(portal, out):
    """ adds a site property to portal_properties"""
    tool = getToolByName(portal, 'portal_properties')
    sheet = tool.site_properties
    if not sheet.hasProperty('webstats_js'):
        sheet.manage_addProperty('webstats_js','','string')
        out.append("Added 'webstats_js' property to site properties")


def addLinkIntegritySwitch(portal, out):
    """ adds a site property to portal_properties """
    tool = getToolByName(portal, 'portal_properties', None)
    if tool is not None:
        sheet = getattr(tool, 'site_properties', None)
        if sheet is not None:
            if not sheet.hasProperty('enable_link_integrity_checks'):
                sheet.manage_addProperty('enable_link_integrity_checks', True, 'boolean')
                out.append("Added 'enable_link_integrity_checks' property to site properties")


def addWebstatsJSFile(portal, out):
    """Add webstats.js for Google Analytics and other trackers support.
    """
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    script = 'webstats.js'
    if jsreg is not None:
        script_ids = jsreg.getResourceIds()
        # Failsafe: first make sure the stylesheet doesn't exist in the list
        if script not in script_ids:
            jsreg.registerScript(script,
                    enabled = True,
                    cookable = True,
                    compression = False)
            try:
                jsreg.moveResourceAfter(script, 'toc.js')
            except ValueError:
                # put it at the bottom of the stack
                jsreg.moveResourceToBottom(script)
            out.append("Added " + script + " to portal_javascipts")


def addTableContents(portal, out):
    """ Adds in table of contents """
    csstool = getToolByName(portal, "portal_css", None)
    if csstool is not None:
        if 'toc.css' not in csstool.getResourceIds():
            csstool.manage_addStylesheet(id="toc.css",rel="stylesheet", enabled=True)
    jstool = getToolByName(portal, "portal_javascripts", None)
    if jstool is not None:
        if 'toc.js' not in jstool.getResourceIds():
            jstool.registerScript(id="toc.js", enabled=True)
    out.append("Added in css and js for table of contents")


def updateMemberSecurity(portal, out):
    pprop = getToolByName(portal, 'portal_properties')
    portal.manage_permission('Add portal member', roles=['Manager','Owner'], acquire=0)
    pprop.site_properties.manage_changeProperties(allowAnonymousViewAbout=False)

    portal.manage_changeProperties(validate_email=True)

    pmembership = getToolByName(portal, 'portal_membership')
    pmembership.memberareaCreationFlag = 0
    out.append("Updated member management security")


def updatePASPlugins(portal, out):
    from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
    from StringIO import StringIO

    sout=StringIO()

    activatePluginInterfaces(portal, 'mutable_properties', sout)
    activatePluginInterfaces(portal, 'source_users', sout)
    activatePluginInterfaces(portal, 'credentials_cookie_auth', sout,
            disable=['ICredentialsResetPlugin', 'ICredentialsUpdatePlugin'])
    if not portal.acl_users.objectIds(['Plone Session Plugin']):
        from plone.session.plugins.session import manage_addSessionPlugin
        manage_addSessionPlugin(portal.acl_users, 'session')
        activatePluginInterfaces(portal, "session", sout)
        out.append("Added Plone Session Plugin.")


def updateSkinsAndSiteConfiglet(portal, out):
    """Use new configlets for the skins and site settings"""
    controlPanel = getToolByName(portal, 'portal_controlpanel', None)
    if controlPanel is not None:
        skins = controlPanel.getActionObject('Plone/PortalSkin')
        site = controlPanel.getActionObject('Plone/PloneReconfig')

        if skins is not None:
            skins.action = Expression('string:${portal_url}/@@skins-controlpanel')
            skins.title = "Themes"
        if site is not None:
            site.action = Expression('string:${portal_url}/@@site-controlpanel')
            site.title = "Site settings"


def updateConfigletTitles(portal, out):
    """Update titles of some configlets"""
    controlPanel = getToolByName(portal, 'portal_controlpanel', None)
    if controlPanel is not None:
        collection = controlPanel.getActionObject('Plone/portal_atct')
        language = controlPanel.getActionObject('Plone/PloneLanguageTool')
        navigation = controlPanel.getActionObject('Plone/NavigationSettings')
        types = controlPanel.getActionObject('Plone/TypesSettings')
        users = controlPanel.getActionObject('Plone/UsersGroups')
        users2 = controlPanel.getActionObject('Plone/UsersGroups2')

        if collection is not None:
            collection.title = "Collection"
        if language is not None:
            language.title = "Language"
        if navigation is not None:
            navigation.title = "Navigation"
        if types is not None:
            types.title = "Types"
        if users is not None:
            users.title = "Users and Groups"
        if users2 is not None:
            users2.title = "Users and Groups"


def addIconsForFilterAndSecurityConfiglets(portal, out):
    """Adds icons for the filter and security configlets."""
    iconsTool = getToolByName(portal, 'portal_actionicons', None)
    filterIcon = False
    securityIcon = False
    if iconsTool is not None:
        for icon in iconsTool.listActionIcons():
            if icon.getActionId() == 'HtmlFilter':
                filterIcon = True
            if icon.getActionId() == 'SecuritySettings':
                securityIcon = True
        if not filterIcon:
            iconsTool.addActionIcon(
                category='controlpanel',
                action_id='HtmlFilter',
                icon_expr='htmlfilter_icon.gif',
                title='Html Filter Settings',
                )
            out.append("Added 'filter' icon to actionicons tool.")
        if not securityIcon:
            iconsTool.addActionIcon(
                category='controlpanel',
                action_id='SecuritySettings',
                icon_expr='lock_icon.gif',
                title='Security Settings',
                )
            out.append("Added 'security' icon to actionicons tool.")


def addFilterAndSecurityConfiglets(portal, out):
    """Add the configlets for the filter and security settings"""
    controlPanel = getToolByName(portal, 'portal_controlpanel', None)
    if controlPanel is not None:
        haveFilter = False
        haveSecurity = False
        for configlet in controlPanel.listActions():
            if configlet.getId() == 'HtmlFilter':
                haveFilter = True
            if configlet.getId() == 'SecuritySettings':
                haveSecurity = True
        if not haveFilter:
            controlPanel.registerConfiglet(id         = 'HtmlFilter',
                                           appId      = 'Plone',
                                           name       = 'HTML Filtering',
                                           action     = 'string:${portal_url}/@@filter-controlpanel',
                                           category   = 'Plone',
                                           permission = ManagePortal,)
            out.append("Added html filter settings to the control panel")
        if not haveSecurity:
            controlPanel.registerConfiglet(id         = 'SecuritySettings',
                                           appId      = 'SecuritySettings',
                                           name       = 'Security',
                                           action     = 'string:${portal_url}/@@security-controlpanel',
                                           category   = 'Plone',
                                           permission = ManagePortal,)
            out.append("Added security settings to the control panel")


def addSitemapProperty(portal, out):
    tool = getToolByName(portal, 'portal_properties', None)
    if tool is not None:
        sheet = getattr(tool, 'site_properties', None)
        if sheet is not None:
            if not sheet.hasProperty('enable_sitemap'):
                sheet.manage_addProperty('enable_sitemap', False, 'boolean')
                out.append("Added 'enable_sitemap' property to site properties")


def updateKukitJS(portal, out):
    """Use the unpacked kukit-src.js and pack it ourself.
    """
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    old_id = '++resource++kukit.js'
    new_id = '++resource++kukit-src.js'
    if jsreg is not None:
        script_ids = jsreg.getResourceIds()
        if old_id in script_ids and new_id in script_ids:
            jsreg.unregisterResource(old_id)
        elif old_id in script_ids:
            jsreg.renameResource(old_id, new_id)
            out.append("Use %s instead of %s" % (new_id, old_id))
        resource = jsreg.getResource(new_id)
        if resource is not None:
            resource.setCompression('full')
            out.append("Set 'full' compression on %s" % new_id)


def addCacheForResourceRegistry(portal, out):
    ram_cache_id = 'ResourceRegistryCache'
    if not ram_cache_id in portal.objectIds():
        RAMCacheManager.manage_addRAMCacheManager(portal, ram_cache_id)
        cache = getattr(portal, ram_cache_id)
        settings = cache.getSettings()
        settings['max_age'] = 24*3600 # keep for up to 24 hours
        settings['request_vars'] = ('URL',)
        cache.manage_editProps('Cache for saved ResourceRegistry files', settings)
        out.append('Created RAMCache %s for ResourceRegistry output' % ram_cache_id)
    reg = getToolByName(portal, 'portal_css', None)
    if reg is not None and getattr(aq_base(reg), 'ZCacheable_setManagerId', None) is not None:
        reg.ZCacheable_setManagerId(ram_cache_id)
        reg.ZCacheable_setEnabled(1)
        out.append('Associated portal_css with %s' % ram_cache_id)
    reg = getToolByName(portal, 'portal_javascripts', None)
    if reg is not None and getattr(aq_base(reg), 'ZCacheable_setManagerId', None) is not None:
        reg.ZCacheable_setManagerId(ram_cache_id)
        reg.ZCacheable_setEnabled(1)
        out.append('Associated portal_javascripts with %s' % ram_cache_id)


def removeTablelessSkin(portal, out):
    st = getToolByName(portal, 'portal_skins')
    if 'Plone Tableless' in st.getSkinSelections():
        st.manage_skinLayers(['Plone Tableless'], del_skin=True)
        out.append("Removed the Plone Tableless skin")
    if st.default_skin=='Plone Tableless':
        st.default_skin='Plone Default'
        out.append("Changed the default skin to 'Plone Default'")


def updateCssQueryJS(portal, out):
    """Compress cssQuery with full-encode like it's supposed to.
    """
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    script_id = 'cssQuery.js'
    if jsreg is not None:
        script_ids = jsreg.getResourceIds()
        resource = jsreg.getResource(script_id)
        if resource is not None:
            resource.setCompression('full-encode')
            out.append("Set 'full-encode' compression on %s" % script_id)


def removeHideAddItemsJS(portal, out):
    """Remove very old javascript.
    """
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    script_id = 'folder_contents_hideAddItems.js'
    if jsreg is not None:
        jsreg.unregisterResource(script_id)
        out.append('Removed %s from portal_javascripts.' % script_id)


def addContentRulesConfiglet(portal, out):
    """Add the configlet for the contentrules settings"""
    controlPanel = getToolByName(portal, 'portal_controlpanel', None)
    if controlPanel is not None:
        haveContentRules = False
        for configlet in controlPanel.listActions():
            if configlet.getId() == 'ContentRulesSettings':
                haveContentRules = True
        if not haveContentRules:
            controlPanel.registerConfiglet(id         = 'ContentRules',
                                           appId      = 'Plone',
                                           name       = 'Content Rules',
                                           action     = 'string:${portal_url}/@@rules-controlpanel',
                                           category   = 'Plone',
                                           permission = 'Content rules: Manage rules',)
            out.append("Added 'Content Rules Settings' to the control panel")


def addIconForContentRulesConfiglet(portal, out):
    """Adds an icon for the maintenance settings configlet. """
    iconsTool = getToolByName(portal, 'portal_actionicons', None)
    if iconsTool is not None:
        for icon in iconsTool.listActionIcons():
            if icon.getActionId() == 'ContentRules':
                break # We already have the icon
        else:
            iconsTool.addActionIcon(
                category='controlpanel',
                action_id='ContentRules',
                icon_expr='contentrules_icon.gif',
                title='Content Rules',
                )
        out.append("Added 'Content Rules Settings' icon to actionicons tool.")


def addObjectProvidesIndex(portal, out):
    """Add the object_provides index to the portal_catalog.
    """
    catalog = getToolByName(portal, 'portal_catalog')
    if 'object_provides' not in catalog.indexes():
        catalog.addIndex('object_provides', 'KeywordIndex')
        out.append("Added object_provides index to portal_catalog")


def removeMyStuffAction(portal, out):
    """The mystuff action is now covered by the dashboard"""
    actions = getToolByName(portal, 'portal_actions')
    if not hasattr(actions, 'user'):
        return
    category=actions.user
    if 'mystuff' in category.objectIds():
        category.manage_delObjects(ids=['mystuff'])
        out.append("Removed the mystuff user action")


def addExternalLinksOpenNewWindowProperty(portal, out):
    """ adds a site property to portal_properties"""
    tool = getToolByName(portal, 'portal_properties')
    sheet = tool.site_properties
    if not sheet.hasProperty('external_links_open_new_window'):
        sheet.manage_addProperty('external_links_open_new_window','false','string')
        out.append("Added 'external_links_open_new_window' property to site properties")


def addMissingWorkflows(portal, out):
    """Add new Plone 3.0 workflows
    """
    wft = getToolByName(portal, 'portal_workflow', None)
    if wft is None:
        return

    new_workflow_ids = [ 'intranet_workflow', 'intranet_folder_workflow',
                        'one_state_workflow', 'simple_publication_workflow']
    encoding = 'utf-8'
    path_prefix = os.path.join(package_home(cmfplone_globals), 'profiles',
            'default', 'workflows')
    
    for wf_id in new_workflow_ids:
        if wf_id in wft.objectIds():
            out.append("Workflow %s already installed; doing nothing" % wf_id)
            continue

        path = os.path.join(path_prefix, wf_id, 'definition.xml')
        body = open(path,'r').read()

        wft._setObject(wf_id, DCWorkflowDefinition(wf_id))
        wf = wft[wf_id]
        wfdc = WorkflowDefinitionConfigurator(wf)

        ( workflow_id
        , title
        , state_variable
        , initial_state
        , states
        , transitions
        , variables
        , worklists
        , permissions
        , scripts
        , description
        ) = wfdc.parseWorkflowXML(body, encoding)

        _initDCWorkflow( wf
                       , title
                       , description
                       , state_variable
                       , initial_state
                       , states
                       , transitions
                       , variables
                       , worklists
                       , permissions
                       , scripts
                       , portal     # not sure what to pass here
                                    # the site or the wft?
                                    # (does it matter at all?)
                      )
        out.append("Added workflow %s" % wf_id)


def addManyGroupsProperty(portal, out):
    """ adds a site property to portal_properties"""
    tool = getToolByName(portal, 'portal_properties')
    sheet = tool.site_properties
    if not sheet.hasProperty('many_groups'):
        sheet.manage_addProperty('many_groups',
                getattr(sheet, 'many_users', False) ,'boolean')
        out.append("Added 'many_groups' property to site properties")


def restorePloneTool(portal, out):
    tool = getToolByName(portal, "plone_utils")
    if tool.meta_type == 'PlonePAS Utilities Tool':
        from Products.CMFPlone.PloneTool import PloneTool
        from Products.CMFDefault.Portal import CMFSite

        # PloneSite has its own security check for manage_delObjects which
        # breaks in the test runner. So we bypass this check.
        CMFSite.manage_delObjects(portal, ['plone_utils'])
        portal._setObject(PloneTool.id, PloneTool())
        out.append("Replaced obsolete PlonePAS version of plone tool with the normal one.")


def updateImportStepsFromBaseProfile(portal, out):
    """Updates the available import steps for existing sites."""

    tool = getToolByName(portal, "portal_setup")
    tool.setBaselineContext("profile-Products.CMFPlone:plone")


def installI18NUtilities(portal, out):
    from plone.app.i18n.locales.interfaces import ICountries
    from plone.app.i18n.locales.countries import Countries

    from plone.app.i18n.locales.interfaces import IContentLanguages
    from plone.app.i18n.locales.languages import ContentLanguages

    from plone.app.i18n.locales.interfaces import IMetadataLanguages
    from plone.app.i18n.locales.languages import MetadataLanguages

    sm = getSiteManager(portal)
    if sm.queryUtility(ICountries) is None:
        sm.registerUtility(Countries(), ICountries)
    if sm.queryUtility(IContentLanguages) is None:
        sm.registerUtility(ContentLanguages(), IContentLanguages)
    if sm.queryUtility(IMetadataLanguages) is None:
        sm.registerUtility(MetadataLanguages(), IMetadataLanguages)

    out.append("Registered plone.app.i18n utilities.")


def addEmailCharsetProperty(portal, out):
    # Add email_charset property
    if not portal.hasProperty('email_charset'):
        portal.manage_addProperty('email_charset', 'utf-8', 'string')
    out.append("Added 'email_charset' property to the portal.")
