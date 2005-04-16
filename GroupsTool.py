from Products.GroupUserFolder.GroupsTool import GroupsTool as BaseTool

from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class GroupsTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.GroupsTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/group.gif'

    # No group workspaces by default
    groupWorkspacesCreationFlag = 0

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

GroupsTool.__doc__ = BaseTool.__doc__

InitializeClass(GroupsTool)
