from Products.CMFDefault.MetadataTool import MetadataTool as BaseTool
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.PloneBaseTool import PloneBaseTool


class MetadataTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone Metadata Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/info_icon.png'


MetadataTool.__doc__ = BaseTool.__doc__

InitializeClass(MetadataTool)
