from Products.GroupUserFolder.GroupsTool import GroupsTool as BaseTool

from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class GroupsTool(BaseTool):

    meta_type = ToolNames.GroupsTool
    security = ClassSecurityInfo()

GroupsTool.__doc__ = BaseTool.__doc__

InitializeClass(GroupsTool)
