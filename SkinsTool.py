from Products.CMFCore.SkinsTool import SkinsTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class SkinsTool(BaseTool):

    meta_type = ToolNames.SkinsTool
    security = ClassSecurityInfo()

SkinsTool.__doc__ = BaseTool.__doc__

InitializeClass(SkinsTool)
