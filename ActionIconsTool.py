from Products.CMFActionIcons.ActionIconsTool import ActionIconsTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class ActionIconsTool(BaseTool):

    meta_type = ToolNames.ActionIconsTool
    security = ClassSecurityInfo()

ActionIconsTool.__doc__ = BaseTool.__doc__

InitializeClass(ActionIconsTool)
