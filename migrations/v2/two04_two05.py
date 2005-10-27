from AccessControl import Permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Acquisition import aq_base

import zLOG


def two04_two05(portal):
    """2.0.4 -> 2.0.5
    """
    out = []
    replaceFolderPropertiesWithEdit(portal, out)
    addFolderListingActionToTopic(portal, out)
    interchangeEditAndSharing(portal, out)
    return out


# Ok, so let's change strategy here. Assume a hostile environment with
# Plone sites misconfigured beyond recognition.

def replaceFolderPropertiesWithEdit(portal, out):
    """rename folder properties tab to edit
    """

    typesTool=getToolByName(portal, 'portal_types')
    typeInfo=typesTool.getTypeInfo('Folder')
    if typeInfo is not None:
        typeObj=getattr(typesTool, typeInfo.getId())
        _actions=typeInfo._cloneActions()
        for action in _actions:
            if action.id=='edit':
                action.title='Edit'
        typeObj._actions=tuple(_actions)

        out.append("Renamed Folder 'properties' tab to 'edit'.")
    return out

def interchangeEditAndSharing(portal, out):
    typesTool=getToolByName(portal, 'portal_types')
    typeInfo=typesTool.getTypeInfo('Folder')
    if typeInfo is not None:
        typeObj=getattr(typesTool, typeInfo.getId())
        _actions=typeInfo._cloneActions()
        i = j = -1
        count = 0
        for action in _actions:
            if action.id=='local_roles':
                i = count
            if action.id=='edit':
                j = count
            count = count+1

        # Don't switch if we couldn't find both actions
        # or the tab order is already correct.
        if -1 < i < j:
            _actions[i], _actions[j] = _actions[j], _actions[i]
            typeObj._actions=tuple(_actions)

        out.append("Interchanged 'edit' and 'sharing' tabs.")
    return out

def addFolderListingActionToTopic(portal, out):
    """CMFTopics don't have a folderlisting action
       causing spurious log messages.
    """
    typesTool=getToolByName(portal, 'portal_types')
    typeInfo=typesTool.getTypeInfo('Topic')
    if typeInfo is not None:
        typeObj=getattr(typesTool, typeInfo.getId())
        _actions=typeInfo._cloneActions()
        for action in _actions:
            if action.id == 'folderlisting':
                break # We already have the action
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

