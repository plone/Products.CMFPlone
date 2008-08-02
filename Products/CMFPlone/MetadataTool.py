from Products.CMFDefault.MetadataTool import MetadataTool as BaseTool
from Products.CMFPlone import ToolNames
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class MetadataTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.MetadataTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/info_icon.gif'

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

MetadataTool.__doc__ = BaseTool.__doc__

InitializeClass(MetadataTool)
