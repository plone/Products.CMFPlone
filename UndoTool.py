from Globals import InitializeClass, DTMLFile
from Products.CMFCore.UndoTool import UndoTool as BaseTool

class UndoTool ( BaseTool ):
    """ This tool is used to undo changes.
    """

    id = 'portal_undo'
    meta_type = 'Plone Undo Tool'

InitializeClass(UndoTool)
