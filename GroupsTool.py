from Products.GroupUserFolder.GroupsTool import GroupsTool as BaseTool

from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class GroupsTool(BaseTool):

    meta_type = ToolNames.GroupsTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/group.gif'

GroupsTool.__doc__ = BaseTool.__doc__

InitializeClass(GroupsTool)
