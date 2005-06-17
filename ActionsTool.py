from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFCore.ActionsTool import ActionsTool as BaseTool
from Products.CMFCore.ActionInformation import oai
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone import ToolNames, FactoryTool
from setup.ConfigurationMethods import correctFolderContentsAction
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

# getOAI() is copied from CMF 1.5
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
# ZPL 2.1
def getOAI(context, object=None):
    request = getattr(context, 'REQUEST', None)
    if request:
        cache = request.get('_oai_cache', None)
        if cache is None:
            request['_oai_cache'] = cache = {}
        info = cache.get( id(object), None )
    else:
        info = None
    if info is None:
        if object is None or not hasattr(object, 'aq_base'):
            folder = None
        else:
            folder = object
            # Search up the containment hierarchy until we find an
            # object that claims it's a folder.
            while folder is not None:
                if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                    # found it.
                    break
                else:
                    # If the parent of the object at hand is a TempFolder
                    # don't strip off its outer acquisition context (Plone)
                    parent = aq_parent(aq_inner(folder))
                    if getattr(parent, '__class__', None) == FactoryTool.TempFolder:
                        folder = aq_parent(folder)
                    else:
                        folder = parent
        info = oai(context, folder, object)
        if request:
            cache[ id(object) ] = info
    return info


class ActionsTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.ActionsTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/confirm_icon.gif'
    
    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

    def __init__(self):
        correctFolderContentsAction(self)

    # overwrite getOAI hook in order to use our method
    def _getOAI(self, context, object):
        return getOAI(context, object)

ActionsTool.__doc__ = BaseTool.__doc__

InitializeClass(ActionsTool)
