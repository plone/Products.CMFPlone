from Products.CMFCore import CMFCorePermissions
from AccessControl import Permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Acquisition import aq_base

import zLOG


def two04_two05(portal):
    """2.0.4 -> 2.0.5
    """
    out = []
    out += replaceFolderPropertiesWithEdit(portal, out)
    out += addFolderListingActionToTopic(portal, out)
    out += interchangeEditAndSharing(portal, out)
    return out


def replaceFolderPropertiesWithEdit(portal, out):
    """rename folder properties tab to edit
    """

    typesTool=getToolByName(portal, 'portal_types')
    typeInfo=typesTool.getTypeInfo('Folder')
    typeObj=getattr(typesTool, typeInfo.getId())
    _actions=typeInfo._cloneActions()
    for action in _actions:
        if action.id=='edit':
            action.title='Edit'
    typeObj._actions=_actions

    out.append("Renamed folder 'properties' tab to 'edit'.")
    return out

def interchangeEditAndSharing(portal, out):
    typesTool=getToolByName(portal, 'portal_types')
    typeInfo=typesTool.getTypeInfo('Folder')
    typeObj=getattr(typesTool, typeInfo.getId())
    _actions=typeInfo._cloneActions()
    count = 0
    for action in _actions:
        if action.id=='local_roles':
            i = count
        if action.id=='edit':
            j = count
        count = count+1
    _actions[i],_actions[j] = _actions[j],_actions[i]
    out.append("Interchanged 'edit' and 'sharing' tabs.")      
    typeObj._actions=_actions 
    return out

def addFolderListingActionToTopic(portal, out):
    """CMFTopics don't have a folderlisting action
       causing spurious log messages.
    """
    typesTool=getToolByName(portal, 'portal_types')
    typeInfo=typesTool.getTypeInfo('Topic')
    typeObj=getattr(typesTool, typeInfo.getId())
    _actions=typeInfo._cloneActions()
    for action in _actions:
        if action.id == 'folderlisting':
            break # we already have the action
    else:
        typeObj.addAction('folderlisting',
            name='Folder Listing',
            action='string:${folder_url}/folder_listing',
            condition='',
            permission='View',
            category='folder',
            visible=0,
            )

    out.append("Added 'folderlisting' action to Topics.")
    return out

