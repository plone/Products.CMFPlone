from Products.CMFCore.CatalogTool import CatalogTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class CatalogTool(BaseTool):

    meta_type = ToolNames.CatalogTool
    security = ClassSecurityInfo()

CatalogTool.__doc__ = BaseTool.__doc__

InitializeClass(CatalogTool)
