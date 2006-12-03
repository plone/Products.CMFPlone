from Globals import InitializeClass
from Products.CMFCore.ActionsTool import ActionsTool as BaseTool
from Products.CMFPlone import ToolNames
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class ActionsTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.ActionsTool
    toolicon = 'skins/plone_images/confirm_icon.gif'

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

InitializeClass(ActionsTool)
