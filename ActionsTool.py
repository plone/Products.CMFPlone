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

class ActionsTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.ActionsTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/confirm_icon.gif'
    
    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )


    # The listFilteredActionsFor method below is derived from the corresponding method in
    # CMFCore/ActionsTool.py from the Zope CMF 1.4.2.  THE METHOD HAS BEEN MODIFIED.
    # This code is licensed under the Zope Public License (see LICENSE.ZPL)
    # This software is Copyright (c) Zope Corporation (tm) and Contributors. 
    # All rights reserved.
    def __init__(self):
        correctFolderContentsAction(self)
    #
    #   'portal_actions' interface methods
    #
    # Overriding listFilteredActionsFor so that it hands the correct 'folder'
    # object to action expressions.
    #
    security.declarePublic('listFilteredActionsFor')
    def listFilteredActionsFor(self, object=None):
        """
        Return a mapping containing of all actions available to the
        user against object, bucketing into categories.
        """
        portal = aq_parent(aq_inner(self))
        if object is None or not hasattr(object, 'aq_base'):
            folder = portal
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
        ec = createExprContext(folder, portal, object)
        actions = []
        append = actions.append
        info = oai(self, folder, object)

        # Include actions from specific tools.
        for provider_name in self.listActionProviders():
            # Skip missing or broken providers (Plone)
            provider = getattr(self, provider_name, None)
            if hasattr(aq_base(provider), 'listActions'):
                self._listActions(append,provider,info,ec)

        # Include actions from object.
        if object is not None:
            base = aq_base(object)
            if hasattr(base, 'listActions'):
                self._listActions(append,object,info,ec)

        # Reorganize the actions by category,
        # filtering out disallowed actions.
        filtered_actions={'user':[],
                          'folder':[],
                          'object':[],
                          'global':[],
                          'workflow':[],
                          }
        for action in actions:
            category = action['category']
            permissions = action.get('permissions', None)
            visible = action.get('visible', 1)
            if not visible:
                continue
            verified = 0
            if not permissions:
                # This action requires no extra permissions.
                verified = 1
            else:
                # startswith() is used so that we can have several
                # different categories that are checked in the object or
                # folder context.
                if (object is not None and
                    (category.startswith('object') or
                     category.startswith('workflow'))):
                    context = object
                elif (folder is not None and
                      category.startswith('folder')):
                    context = folder
                else:
                    context = portal
                for permission in permissions:
                    # The user must be able to match at least one of
                    # the listed permissions.
                    if _checkPermission(permission, context):
                        verified = 1
                        break
            if verified:
                catlist = filtered_actions.setdefault(category, [])
                # XXX Dieter says the check below is unnecessary and very slow,
                # so away it goes.
                # Filter out duplicate actions by identity...
                # if not action in catlist:
                catlist.append(action)
                # ...should you need it, here's some code that filters
                # by equality (use instead of the two lines above)
                #if not [a for a in catlist if a==action]:
                #    catlist.append(action)
        return filtered_actions

    # listFilteredActions() is an alias.
    security.declarePublic('listFilteredActions')
    listFilteredActions = listFilteredActionsFor

ActionsTool.__doc__ = BaseTool.__doc__

InitializeClass(ActionsTool)
