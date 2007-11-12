from Products.CMFCore.UndoTool import UndoTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class UndoTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.UndoTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/undo_icon.gif'

UndoTool.__doc__ = BaseTool.__doc__

InitializeClass(UndoTool)
