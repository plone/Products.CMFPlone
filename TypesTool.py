from Products.CMFCore.TypesTool import TypesTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class TypesTool(BaseTool):

    meta_type = ToolNames.TypesTool
    security = ClassSecurityInfo()

TypesTool.__doc__ = BaseTool.__doc__

InitializeClass(TypesTool)
