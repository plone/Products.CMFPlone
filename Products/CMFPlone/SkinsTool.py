from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore.SkinsTool import SkinsTool as BaseTool
from Products.CMFPlone.PloneBaseTool import PloneBaseTool


class SkinsTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone Skins Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/skins_icon.png'

    default_skin = ''
    request_varname = 'plone_skin'


SkinsTool.__doc__ = BaseTool.__doc__

InitializeClass(SkinsTool)
