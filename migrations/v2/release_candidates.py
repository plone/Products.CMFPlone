from Products.CMFCore import CMFCorePermissions
from AccessControl import Permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.setup.ConfigurationMethods import correctFolderContentsAction
from Products.CMFCore.Expression import Expression
from Acquisition import aq_base
from plone2_base import addCatalogIndexes

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
    return []

def rc3_rc4(portal):
    out=[]

    pt=getToolByName(portal, 'portal_properties')
    _actions=pt._cloneActions()
    for action in _actions:
        if action.id=='configPortal':
            action.visible=0
            out.append('Setting portal_properties configPortal action.visible to 0')
    pt._actions=_actions

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

    out.append('Adding AddToFavorites to portal_actions and portal_actionicons')
    ai=getToolByName(portal, 'portal_actionicons')
    try:
        ai.addActionIcon('plone', 'addtofavorites', 'site_icon.gif', 'AddToFavorites')
    except KeyError:
        pass #Duplicate definition!

    tt=getToolByName(portal, 'portal_types')
    for ptype in tt.objectValues():
        if ptype.getId() not in ('Folder', 'Large Plone Folder') and \
          'local_roles' not in [ai.getId() for ai in ptype.listActions()]:
            ptype.addAction('local_roles',
                     name='Sharing',
                     action="string:${object_url}/folder_localrole_form",
                     condition='',
                     permission='Manage properties',
                     category='object')
        actions = ()
        try:
            _actions = ptype._cloneActions()
        except AttributeError:
            # Stumbled across ancient dictionary actions
            if not hasattr(aq_base(ptype), '_convertActions'):
                out.append(('Can\'t convert actions of %s! Jumping to next action.' % ptype.getId(), zLOG.ERROR))
                # XXX that's bad :[
                continue
            ptype._convertActions()
            _actions = ptype._cloneActions()

        for action in _actions:
            if action.getId()=='metadata':
                 action.title='Properties'
            if action.getId()=='content_status_history':
                 action.visible=0
        ptype._actions = _actions

    if 'addtofavorites' not in [action.getId() for action in at.listActions()]:
        at.addAction('addtofavorites',
                     'Add to Favorites',
                     'string:${request/URL1}/addtoFavorites',
                     'member',
                     'View',
                     'document_actions')

    mt=getToolByName(portal, 'portal_membership')
    _actions=mt._cloneActions()
    for action in _actions:
        if action.id=='preferences':
            out.append('Setting action of portal_membership preferences')
            action.action=Expression('string:${portal_url}/plone_memberprefs_panel')
    mt._actions=_actions

    return out
    
def rc4_rc5(portal):
    #fix 'local_roles' properties
    out=[]
    typestool=getToolByName(portal, 'portal_types')
    for typeobj in typestool.objectValues():
        _actions = typeobj._cloneActions()
        for action in _actions:
            if action.id=='local_roles':
                action.title='Sharing'
        typeobj._actions = _actions
    out.append('Change local_roles label to Sharing')
    
    return out
 
def rc5_final(portal):
    out = []

    at=getToolByName(portal, 'portal_actions')
    hasFavorites=0
    _actions = at._cloneActions()
    for action in _actions:
        if action.getId() == 'addtofavorites':
            if hasFavorites:
                del action
                out.append('Removed doubled add to favorites action')
            else:
                hasFavorites=1
    at._actions=_actions

    out.append('Added Plone Tabless skin')
    addTablelessSkin(portal)

    out.append('Adding in Plone 2 base')
    addCatalogIndexes(portal)
    return out

def addTablelessSkin(portal):
    st = getToolByName(portal, 'portal_skins')
    defaultName = 'Plone Default'
    tablelessName = 'Plone Tableless'
    path = []
    selections = st._getSelections()

    if selections.has_key(defaultName):
        for p in st._getSelections()[defaultName].split(','):
            if p == 'plone_templates':
                path.append('plone_tableless')
            path.append(p)
    
    st.manage_skinLayers(add_skin=1, skinname=tablelessName, skinpath=path)
