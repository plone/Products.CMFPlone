from zope.component import queryUtility

from Products.CMFCore.interfaces import IActionsTool
from Products.CMFActionIcons.interfaces import IActionIconsTool
from Products.CMFCore.interfaces import ITypesTool
from Products.ResourceRegistries.interfaces import IKSSRegistry, IJSRegistry
from Products.CMFCore.Expression import Expression
from Products.CMFPlone.migrations.migration_util import loadMigrationProfile
from Products.CMFCore.utils import getToolByName
from alphas import addContentRulesAction

from Acquisition import aq_base

def beta1_beta2(portal):
    """ 3.0-beta1 -> 3.0-beta2
    """

    out = []

    migrateHistoryTab(portal, out)

    changeOrderOfActionProviders(portal, out)
    updateEditActionConditionForLocking(portal, out)
    addOnFormUnloadJS(portal, out)

    # Add the action a second time, now to the correct action category
    addContentRulesAction(portal, out)

    cleanupOldActions(portal, out)

    cleanDefaultCharset(portal, out)

    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.0b1-3.0b2')

    addAutoGroupToPAS(portal, out)

    removeS5Actions(portal, out)

    addCacheForKSSRegistry(portal, out)

    modifyKSSResources(portal, out)

    addContributorToCreationPermissions(portal, out)

    return out


def beta2_beta3(portal):
    """ 3.0-beta2 -> 3.0-beta3
    """

    out = []

    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.0b2-3.0b3')

    removeSharingAction(portal, out)
    
    addEditorToSecondaryEditorPermissions(portal, out)

    return out


def beta3_beta4(portal):
    """ 3.0-beta3 -> 3.0-beta4
    """

    out = []

    return out


def migrateHistoryTab(portal, out):
    portal_actions = queryUtility(IActionsTool)
    if portal_actions is not None:
        objects = getattr(portal_actions, 'object', None)
        if objects is not None:
            if 'rss' in objects.objectIds():
                objects.manage_renameObjects(['rss'], ['history'])
                out.append('Migrated history action.')


def changeOrderOfActionProviders(portal, out):
    portal_actions = queryUtility(IActionsTool)
    if portal_actions is not None:
        portal_actions.deleteActionProvider('portal_actions')
        portal_actions.addActionProvider('portal_actions')
        out.append('Changed the order of action providers.')

def cleanupOldActions(portal, out):
    portal_actions = queryUtility(IActionsTool)
    if portal_actions is not None:
        # Remove some known unused actions from the object_tabs category and
        # remove the category completely if no actions are left
        object_tabs = getattr(portal_actions, 'object_tabs', None)
        if object_tabs is not None:
            if 'contentrules' in object_tabs.objectIds():
                object_tabs._delObject('contentrules')
            if 'change_ownership' in object_tabs.objectIds():
                object_tabs._delObject('change_ownership')
            if len(object_tabs.objectIds()) == 0:
                del object_tabs
                portal_actions._delObject('object_tabs')
                out.append('Removed object_tabs action category.')
        object_ = getattr(portal_actions, 'object', None)
        if object_ is not None:
            if 'reply' in object_.objectIds():
                object_._delObject('reply')
        user = getattr(portal_actions, 'user', None)
        if user is not None:
            if 'logged_in' in user.objectIds():
                user._delObject('logged_in')
            if 'myworkspace' in user.objectIds():
                user._delObject('myworkspace')
        global_ = getattr(portal_actions, 'global', None)
        if global_ is not None:
            if 'manage_members' in global_.objectIds():
                global_._delObject('manage_members')
            if 'configPortal' in global_.objectIds():
                global_._delObject('configPortal')
            if len(global_.objectIds()) == 0:
                del global_
                portal_actions._delObject('global')
                out.append('Removed global action category.')

def cleanDefaultCharset(portal, out):
    charset = portal.getProperty('default_charset', None)
    if charset is not None:
        if not charset.strip():
            portal.manage_delProperties(['default_charset'])
            out.append('Removed empty default_charset portal property')


def addAutoGroupToPAS(portal, out):
    from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
    from StringIO import StringIO

    sout=StringIO()

    if not portal.acl_users.objectIds(['Automatic Group Plugin']):
        from Products.PlonePAS.plugins.autogroup import manage_addAutoGroup
        manage_addAutoGroup(portal.acl_users, 'auto_group',
                'Automatic Group Provider',
                'AuthenticatedUsers", "Authenticated Users (Virtual Group)')
        activatePluginInterfaces(portal, "auto_group", sout)
        out.append("Added automatic group PAS plugin")

def removeS5Actions(portal, out):
    portalTypes = queryUtility(ITypesTool)
    if portalTypes is not None:
        document = portalTypes.restrictedTraverse('Document', None)
        if document:
            ids = [x.getId() for x in document.listActions()]
            if 's5_presentation' in ids:
                index = ids.index('s5_presentation')
                document.deleteActions([index])
                out.append("Removed 's5_presentation' action from actions tool.")

    iconsTool = queryUtility(IActionIconsTool)
    if iconsTool is not None:
        ids = [x.getActionId() for x in iconsTool.listActionIcons()]
        if 's5_presentation' in ids:
            iconsTool.removeActionIcon('plone','s5_presentation')
            out.append("Removed 's5_presentation' icon from actionicons tool.")

def addCacheForKSSRegistry(portal, out):
    ram_cache_id = 'ResourceRegistryCache'
    reg = queryUtility(IKSSRegistry)
    if reg is not None and getattr(aq_base(reg), 'ZCacheable_setManagerId', None) is not None:
        reg.ZCacheable_setManagerId(ram_cache_id)
        reg.ZCacheable_setEnabled(1)
        out.append('Associated portal_kss with %s' % ram_cache_id)

def modifyKSSResources(portal, out):
    # make kukit.js conditonol and not load for anonymous
    reg = queryUtility(IJSRegistry)
    if reg is not None:
        id = '++resource++kukit-src.js'
        entry = aq_base(reg).getResourcesDict().get(id, None)
        if entry:
            reg.updateScript(id, expression='not:here/@@plone_portal_state/anonymous')
            out.append('Updated kss javascript resource %s, to disable kss for anonymous.' % id)
    # register the new kss resources
    reg = queryUtility(IKSSRegistry)
    if reg is not None:
        new_resources = ['at_experimental.kss', 'plone_experimental.kss']
        for id in new_resources:
            entry = aq_base(reg).getResourcesDict().get(id, None)
            if not entry:
                reg.registerKineticStylesheet(id, enabled=0)
                out.append('Added kss resource %s, disabled by default.' % id)

def addContributorToCreationPermissions(portal, out):
    
    if 'Contributor' not in portal.valid_roles():
        portal._addRole('Contributor')
    if 'Contributor' not in portal.acl_users.portal_role_manager.listRoleIds():
        portal.acl_users.portal_role_manager.addRole('Contributor')
    
    for p in ['Add portal content', 'Add portal folders', 'ATContentTypes: Add Document',
                'ATContentTypes: Add Event', 'ATContentTypes: Add Favorite',
                'ATContentTypes: Add File', 'ATContentTypes: Add Folder', 
                'ATContentTypes: Add Image', 'ATContentTypes: Add Large Plone Folder',
                'ATContentTypes: Add Link', 'ATContentTypes: Add News Item', ]:
        roles = [r['name'] for r in portal.rolesOfPermission(p) if r['selected']]
        if 'Contributor' not in roles:
            roles.append('Contributor')
            portal.manage_permission(p, roles, bool(portal.acquiredRolesAreUsedBy(p)))

def removeSharingAction(portal, out):
    portal_types = getToolByName(portal, 'portal_types', None)
    if portal_types is not None:
        for fti in portal_types.objectValues():
            action_ids = [a.id for a in fti.listActions()]
            if 'local_roles' in action_ids:
                fti.deleteActions([action_ids.index('local_roles')])
                
    out.append('Removed explicit references to sharing action')
    
def addEditorToSecondaryEditorPermissions(portal, out):
    
    for p in ['Manage properties', 'Modify view template', 'Request review']:
        roles = [r['name'] for r in portal.rolesOfPermission(p) if r['selected']]
        if 'Editor' not in roles:
            roles.append('Editor')
            portal.manage_permission(p, roles, bool(portal.acquiredRolesAreUsedBy(p)))

def updateEditActionConditionForLocking(portal, out):
    """
    Condition on edit views for Document, Event, File, Folder, Image, 
    Large_Plone_Folder, Link, Topic has been added to not display the Edit
    tab if an item is locked
    """
    portal_types = queryUtility(ITypesTool)
    lockable_types = ['Document', 'Event', 'Favorite', 'File', 'Folder',
                      'Image', 'Large Plone Folder', 'Link',
                      'News Item', 'Topic']
    if portal_types is not None:
        for contentType in lockable_types:
            fti = portal_types.getTypeInfo(contentType)
            if fti:
                for action in fti.listActions():
                    if action.getId() == 'edit' and not action.condition:
                        action.condition = Expression("not:object/@@plone_lock_info/is_locked_for_current_user|python:True")

def addOnFormUnloadJS(portal, out):
    """
    add the form unload JS to the js registry
    """
    jsreg = queryUtility(IJSRegistry)
    script = 'unlockOnFormUnload.js'
    if jsreg is not None:
        script_ids = jsreg.getResourceIds()
        # Failsafe: first make sure the stylesheet doesn't exist in the list
        if script not in script_ids:
            jsreg.registerScript(script,
                                 enabled = True,
                                 cookable = True)
            # put it at the bottom of the stack
            jsreg.moveResourceToBottom(script)
            out.append("Added " + script + " to portal_javascipt")

