from Products.CMFActionIcons.ActionIconsTool import ActionIconsTool as BaseTool
from Products.CMFActionIcons.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class ActionIconsTool(BaseTool):

    meta_type = ToolNames.ActionIconsTool
    security = ClassSecurityInfo()

    security.declareProtected(View, 'renderActionIcon')
    def renderActionIcon( self, 
                          category,
                          action_id,
                          default=None,
                          context=None ):
        """ Returns the actual object for the icon.  If you
            pass in a path elements in default it will attempt
            to traverse to that path.  Otherwise it will return
            None
        """ 
        icon = self.queryActionIcon( category,
                                     action_id,
                                     default=default,
                                     context=context )
        if icon is not None:
            portal=getToolByName(self, 'portal_url').getPortalObject()
            return portal.restrictedTraverse(icon)

        return default     
               
ActionIconsTool.__doc__ = BaseTool.__doc__

InitializeClass(ActionIconsTool)
