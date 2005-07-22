from Products.CMFCore import CMFCorePermissions
from AccessControl import Permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.setup.ConfigurationMethods import correctFolderContentsAction
from Products.CMFCore.Expression import Expression
from Acquisition import aq_base
from oneX_twoBeta2 import addPloneTableless
from plone2_base import addCatalogIndexes
from Products.CMFPlone.migrations.migration_util import saveCloneActions, cleanupSkinPath
import zLOG

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

    out.append('Renaming control panel to \'portal_controlpanel\'')
    if hasattr(aq_base(portal), 'portal_control_panel_actions'):
        at.deleteActionProvider('portal_control_panel_actions')
        portal.manage_renameObject('portal_control_panel_actions', 'portal_controlpanel')
        at.addActionProvider('portal_controlpanel')

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
        ai.addActionIcon('plone', 'addtofavorites', 'favorite_icon.gif', 'AddToFavorites')
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
        success, retval = saveCloneActions(ptype)
        if success:
            _actions = retval
        else:
            out.append(retval)
            continue

        for action in _actions:
            if action.getId()=='metadata':
                action.title='Properties'
            if action.getId()=='content_status_history':
                action.visible=0
        ptype._actions = _actions

    if 'addtofavorites' not in [action.getId() for action in at.listActions()]:
        at.addAction('addtofavorites',
                     'Add to Favorites',
                     'string:${object_url}/addtoFavorites',
                     'member',
                     'View',
                     'document_actions',
                     visible=0)

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
        success, retval = saveCloneActions(typeobj)
        if success:
            _actions = retval
        else:
            out.append(retval)
            continue

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

    out.append('Added Plone Tableless skin')
    addTablelessSkin(portal)

    out.append('Adding in catalog indexes')
    addCatalogIndexes(portal)

    out.append('Adding new properties: typesLinkToFolderContents, typesLinkToFolderContentsInFC')
    addFolderContentsProperties(portal)

    out.append('Removing deprecated property: use_folder_contents')
    delOldFolderContentsProperty(portal)

    return out

def rc5_rc6(portal):
    removeTypesForcedFolderContents(portal)
    # changeCopyPermission(portal)

def final_rc6(portal):
    out = []
    out.append('Assigning folder_workflow to Large Plone Folder')
    fixupLargePloneFolderWorkflow(portal)
    return out

def fixupLargePloneFolderWorkflow(portal):
    # Large Plone Folder should use folder_workflow
    wf_tool = getToolByName(portal, 'portal_workflow')
    lpf_chain = list(wf_tool.getChainFor('Large Plone Folder'))
    if 'plone_workflow' in lpf_chain:
        lpf_chain.remove('plone_workflow')
    if 'folder_workflow' not in lpf_chain:
        lpf_chain.append('folder_workflow')
    wf_tool.setChainForPortalTypes(('Large Plone Folder',), ', '.join(lpf_chain))

def changeCopyPermission(portal):
    _actions = portal.portal_actions._cloneActions()
    for action in _actions:
        if action.id=='copy':
            expr='python:portal.portal_membership.checkPermission("%s", object)' % \
                 CMFCorePermissions.ModifyPortalContent
            action.condition=Expression(expr)
    portal.portal_actions._actions=_actions

def removeTypesForcedFolderContents(portal):
    pp=getToolByName(portal,'portal_properties')
    p = getattr(pp , 'navtree_properties', None)

    if props.hasProperty('removeTypesForcedFolderContents(portal)'):
        props._delProperty('removeTypesForcedFolderContents(portal)')

def addFolderContentsProperties(portal):
    """Existing use_folder_contents split into two new properties:

    site_properties/typesLinkToFolderContentsInFC:
      when looking at folder_contents, what content types should be linked to /folder_contents,
      as opposed to their 'view' link?
    navtree_properties/typesLinkToFolderContents:
      for quick navigation in navigation slot, what types should always show as link to /f_c,
      (assuming you have perm, etc.)
    """

    props = portal.portal_properties.navtree_properties
    if not hasattr(props, 'typesLinkToFolderContents'):
        props._setProperty('typesLinkToFolderContents', [], 'lines')
    props = portal.portal_properties.site_properties
    ufc = []
    if hasattr(props, 'use_folder_contents'):
        ufc = props.use_folder_contents
    if not ufc:
        ufc = ['Folder','Large Plone Folder']
    if not hasattr(props, 'typesLinkToFolderContentsInFC'):
        props._setProperty('typesLinkToFolderContentsInFC', ufc, 'lines')

def delOldFolderContentsProperty(portal):
    """This was an overly-vague name, which got us into a mess as people overloaded it."""

    props = portal.portal_properties.site_properties
    if hasattr(props, 'use_folder_contents'):
        props._delProperty('use_folder_contents')

def addTablelessSkin(portal):
    # to be shure that we have a plone_tableless directory view
    from oneX_twoBeta2 import addPloneTableless
    addPloneTableless(portal)
    st = getToolByName(portal, 'portal_skins')
    defaultName = 'Plone Default'
    cleanupSkinPath(portal, defaultName)
    tablelessName = 'Plone Tableless'
    path = []
    selections = st._getSelections()

    if selections.has_key(defaultName):
        for p in selections[defaultName].split(','):
            if p == 'plone_templates':
                path.append('plone_tableless')
            path.append(p)

    st.manage_skinLayers(add_skin=1, skinname=tablelessName, skinpath=path)

def rc6_finalfinal(portal):
    pass
