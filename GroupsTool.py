from Products.GroupUserFolder.GroupsTool import GroupsTool as BaseTool

from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from utils import base_hasattr

class GroupsTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.GroupsTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/group.gif'

    # No group workspaces by default
    groupWorkspacesCreationFlag = 0

    security.declarePublic('getGroupInfo')
    def getGroupInfo(self, groupId):
        """
        Return default group info of any group
        """
        group = self.getGroupById(groupId)

        if group is None:
            return None

        groupinfo = { 'title'    : group.getProperty('title'),
                      'description' : group.getProperty('description'),
                    }

        return groupinfo

    def createGrouparea(self, id):
        """
        Override the method to make sure the groups folder gets indexed,
        GRUF makes a policy decision to unindex the groups folder.
        """
        workspaces = self.getGroupWorkspacesFolder()
        BaseTool.createGrouparea(self, id)
        if workspaces is None:
            workspaces = self.getGroupWorkspacesFolder()
            if base_hasattr(workspaces, 'reindexObject'):
                workspaces.reindexObject()

GroupsTool.__doc__ = BaseTool.__doc__

InitializeClass(GroupsTool)
