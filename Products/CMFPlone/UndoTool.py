from Products.CMFCore.UndoTool import UndoTool as BaseTool
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool


class UndoTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone Undo Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/undo_icon.png'

UndoTool.__doc__ = BaseTool.__doc__

InitializeClass(UndoTool)
