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
    out += replaceFolderPropertiesToEdit(portal, out)
    
    return out

def replaceFolderPropertiesToEdit(portal, out):
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
