from Products.CMFCore.ActionsTool import ActionsTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from setup.ConfigurationMethods import correctFolderContentsAction

class ActionsTool(BaseTool):

    meta_type = ToolNames.ActionsTool
    security = ClassSecurityInfo()

    def __init__(self):
        correctFolderContentsAction(self)

ActionsTool.__doc__ = BaseTool.__doc__

InitializeClass(ActionsTool)
