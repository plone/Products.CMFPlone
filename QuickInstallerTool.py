from Products.CMFQuickInstallerTool import AlreadyInstalled
from Products.CMFQuickInstallerTool.QuickInstallerTool \
   import QuickInstallerTool as BaseTool

from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class QuickInstallerTool(BaseTool):
    """ A tool to ease installing/uninstalling all sorts of products """

    meta_type = ToolNames.QuickInstallerTool
    security = ClassSecurityInfo()

QuickInstallerTool.__doc__ = BaseTool.__doc__

InitializeClass(QuickInstallerTool)
