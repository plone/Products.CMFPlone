from Products.CMFQuickInstallerTool.QuickInstallerTool \
   import QuickInstallerTool as BaseTool
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class QuickInstallerTool(PloneBaseTool, BaseTool):
    """ A tool to ease installing/uninstalling all sorts of products """

    meta_type = ToolNames.QuickInstallerTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/product_icon.gif'

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

QuickInstallerTool.__doc__ = BaseTool.__doc__

InitializeClass(QuickInstallerTool)
