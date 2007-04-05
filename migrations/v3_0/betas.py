from zope.component import queryUtility
from zope.component import getUtility

from Products.CMFCore.interfaces import IActionsTool
from Products.CMFActionIcons.interfaces import IActionIconsTool
from Products.CMFCore.interfaces import ITypesTool
from Products.ResourceRegistries.interfaces import ICSSRegistry
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFPlone.migrations.migration_util import loadMigrationProfile
from alphas import addContentRulesAction


def beta1_beta2(portal):
    """ 3.0-beta1 -> 3.0-beta2
    """

    out = []

    migrateHistoryTab(portal, out)

    changeOrderOfActionProviders(portal, out)

    # Add the action a second time, now to the correct action category
    addContentRulesAction(portal, out)

    cleanupOldActions(portal, out)

    cleanDefaultCharset(portal, out)

    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.0b1-3.0b2')

    addAutoGroupToPAS(portal, out)

    removeS5Actions(portal, out)

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
