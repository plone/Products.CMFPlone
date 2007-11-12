from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFCore.SkinsTool import SkinsTool as BaseTool
from Products.CMFPlone import ToolNames
from Products.CMFPlone.PloneBaseTool import PloneBaseTool


class SkinsTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.SkinsTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/skins_icon.gif'

    default_skin = ''
    request_varname = 'plone_skin'


SkinsTool.__doc__ = BaseTool.__doc__

InitializeClass(SkinsTool)
