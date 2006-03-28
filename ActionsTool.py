from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.CMFCore.ActionsTool import ActionsTool as BaseTool
from Products.CMFPlone import ToolNames
from setup.ConfigurationMethods import correctFolderContentsAction
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFCore.interfaces.portal_actions \
     import ActionProvider as IActionProvider

_marker = object()

class ActionsTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.ActionsTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/confirm_icon.gif'

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

    def __init__(self):
        correctFolderContentsAction(self)

    def _getActions(self, provider_name, actions, object):
        """
        gracefully omit broken or missing providers
        """
        provider = getattr(self, provider_name, None)

        if provider is None:
            return

        if IActionProvider.isImplementedBy(provider):
            actions.extend( provider.listActionInfos(object=object) )
        elif hasattr(aq_base(provider), 'listActions'):
            # for Action Providers written for CMF versions before 1.5
            actions.extend( self._listActionInfos(provider, object) )

    security.declarePublic('listFilteredActionsFor')
    def listFilteredActionsFor(self, object=None):
        """ List all actions available to the user.
        """
        actions = []

        # Include actions from specific tools.
        [self._getActions(provider_name, actions, object) \
         for provider_name in self.listActionProviders()]

        # Include actions from object.
        if object is not None:
            base = aq_base(object)
            if IActionProvider.isImplementedBy(base):
                actions.extend( object.listActionInfos(object=object) )
            elif hasattr(base, 'listActions'):
                # for objects written for CMF versions before 1.5
                actions.extend( self._listActionInfos(object, object) )

        # Reorganize the actions by category.
        filtered_actions={'user':[],
                          'folder':[],
                          'object':[],
                          'global':[],
                          'workflow':[],
                          }

        for action in actions:
            catlist = filtered_actions.setdefault(action['category'], [])
            catlist.append(action)

        return filtered_actions

ActionsTool.__doc__ = BaseTool.__doc__

InitializeClass(ActionsTool)
