from Products.CMFCore.ActionsTool import ActionsTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class ActionsTool(BaseTool):

    meta_type = ToolNames.ActionsTool
    security = ClassSecurityInfo()

ActionsTool.__doc__ = BaseTool.__doc__

InitializeClass(ActionsTool)
