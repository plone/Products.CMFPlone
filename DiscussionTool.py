from Products.CMFCore.DiscussionTool import DiscussionTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class DiscussionTool(BaseTool):

    meta_type = ToolNames.DiscussionTool
    security = ClassSecurityInfo()

DiscussionTool.__doc__ = BaseTool.__doc__

InitializeClass(DiscussionTool)
