from Products.CMFCore import CMFCorePermissions
from AccessControl import Permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.setup.ConfigurationMethods import correctFolderContentsAction
from Products.CMFCore.Expression import Expression

_permMap = {
    'rename' : CMFCorePermissions.AddPortalContent,
    'copy' : Permissions.view_management_screens,
    'paste' : CMFCorePermissions.AddPortalContent,
    'delete' : Permissions.delete_objects,
    }

_condMap = {
    'cut' : 'python:portal.portal_membership.checkPermission("Delete objects", object)',
    'copy': 'python:portal.portal_membership.checkPermission("%s", object)' % Permissions.copy_or_move,
    }

def rc2_rc3(portal):
    # this migration was never written so all code went to rc3_rc4
    pass

def rc3_rc4(portal):
    out=[]
    #
    pt=getToolByName(portal, 'portal_properties')
    _actions=pt._cloneActions()
    for action in _actions:
        if action.id=='configPortal':
            action.visible=0
            out.append('Setting portal_properties configPortal action.visible to 0')
    pt._actions=_actions

    #
    at=getToolByName(portal, 'portal_actions')
    out.append('Fixing folder contents action')
    correctFolderContentsAction(at)
    _actions=at._cloneActions()
    for action in _actions:
        if action.id in _permMap.keys():
           out.append('Setting permission of portal_actions %s to %s' % (action.id, _permMap[action.id]))
           action.permission = _permMap[action.id]
        if action.id in _condMap.keys():
           out.append('Setting condition of portal_actions %s to %s' % (action.id, _condMap[action.id]))
           action.condition = Expression(_condMap[action.id])
    at._actions=_actions    

    #
    out.append('Adding local_roles action to portal_actions')
    at.addAction('local_roles',
                 name='Sharing',
                 action="string:${object_url}/folder_localrole_form",
                 condition='',
                 permission='Manage properties',
                 category='object')

    #
    out.append('Adding AddToFavorites to portal_actions and portal_actionicons')
    ai=getToolByName(portal, 'portal_actionicons')
    ai.addActionIcon('plone', 'addtofavorites', 'site_icon.gif', 'AddToFavorites')
    at.addAction('addtofavorites',
                 'Add to Favorites',
                 'string:${request/URL1}/addtoFavorites',
                 'member',
                 'View',
                 'document_actions')

    #
    mt=getToolByName(portal, 'portal_membership')
    _actions=mt._cloneActions()
    for action in _actions:
        if action.id=='preferences':
            out.append('Setting action of portal_membership preferences')
            action.action=Expression('string:${portal_url}/plone_memberprefs_panel')
    mt._actions=_actions

    #
    tt=getToolByName(portal, 'portal_types')
    out.append('Removing local_roles from portal_types')
    tt._actions=[a for a in tt._cloneActions() if a.id!='local_roles']
    
def rc4_final(portal):
    out = []