from Products.CMFCore.TypesTool import TypesTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class TypesTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.TypesTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/document_icon.gif'
    
    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

TypesTool.__doc__ = BaseTool.__doc__

InitializeClass(TypesTool)
