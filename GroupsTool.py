from Products.GroupUserFolder.GroupsTool import GroupsTool as BaseTool

from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.utils import classImplements

class GroupsTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.GroupsTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/group.gif'

    # No group workspaces by default
    groupWorkspacesCreationFlag = 0

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )


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

GroupsTool.__doc__ = BaseTool.__doc__

classImplements(GroupsTool, GroupsTool.__implements__)
InitializeClass(GroupsTool)
