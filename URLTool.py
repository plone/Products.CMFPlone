from Products.CMFCore.URLTool import URLTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class URLTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.URLTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/link_icon.gif'
    
    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

URLTool.__doc__ = BaseTool.__doc__

InitializeClass(URLTool)
