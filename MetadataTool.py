from Products.CMFDefault.MetadataTool import MetadataTool as BaseTool
from Products.CMFPlone import ToolNames
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

class MetadataTool(BaseTool):

    meta_type = ToolNames.MetadataTool
    security = ClassSecurityInfo()

MetadataTool.__doc__ = BaseTool.__doc__

InitializeClass(MetadataTool)
