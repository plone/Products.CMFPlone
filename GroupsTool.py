from Products.GroupUserFolder.GroupsTool import GroupsTool as BaseTool

from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneUtilities import ToolIconOverride

class GroupsTool(BaseTool, ToolIconOverride):

    meta_type = ToolNames.GroupsTool
    security = ClassSecurityInfo()
    iconlist = ["group.gif",]

GroupsTool.__doc__ = BaseTool.__doc__

InitializeClass(GroupsTool)
