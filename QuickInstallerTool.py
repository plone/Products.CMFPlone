from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFCore.utils import registerToolInterface
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone import ToolNames
from Products.CMFQuickInstallerTool.QuickInstallerTool \
   import QuickInstallerTool as BaseTool
from Products.CMFQuickInstallerTool.interfaces import IQuickInstallerTool


class QuickInstallerTool(PloneBaseTool, BaseTool):
    """ A tool to ease installing/uninstalling all sorts of products """

    meta_type = ToolNames.QuickInstallerTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/product_icon.gif'

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

QuickInstallerTool.__doc__ = BaseTool.__doc__

InitializeClass(QuickInstallerTool)
registerToolInterface('portal_quickinstaller', IQuickInstallerTool)
