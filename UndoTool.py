from Products.CMFCore.UndoTool import UndoTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class UndoTool(BaseTool):

    meta_type = ToolNames.UndoTool
    security = ClassSecurityInfo()

UndoTool.__doc__ = BaseTool.__doc__

InitializeClass(UndoTool)
