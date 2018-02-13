# -*- coding: utf-8 -*-
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
import pkg_resources


# *IF* the base tool is still there, it seems nice to inherit from it.
try:
    pkg_resources.get_distribution('Products.CMFQuickInstallerTool')
except pkg_resources.DistributionNotFound:
    class QuickInstallerTool(PloneBaseTool):
        """ A tool to ease installing/uninstalling all sorts of products

        In Plone 5.2 the extra methods were moved to
        Products.CMFQuickInstallerTool.

        This tool is no longer used in Plone 6, but we will
        keep the class so we can cleanly uninstall and remove this.

        Remove this file in Plone 7.
        """
        pass
else:
    from Products.CMFQuickInstallerTool.QuickInstallerTool \
        import QuickInstallerTool as BaseTool

    class QuickInstallerTool(PloneBaseTool, BaseTool):
        pass
    QuickInstallerTool.__doc__ = BaseTool.__doc__
