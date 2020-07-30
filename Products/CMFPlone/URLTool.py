# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from Products.CMFCore.URLTool import URLTool as BaseTool
from Products.CMFPlone.PloneBaseTool import PloneBaseTool


class URLTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone URL Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/link_icon.png'

    @security.public
    def isURLInPortal(self, url, context=None):
        # Note: no docstring, because the method is publicly available
        # but does not need to be callable on site-url/portal_url/isURLInPortal.
        #
        # This method is overridden by Products.isurlinportal,
        # but the public declaration still seems needed.
        #
        # Also, in tests/testURLTool.py we do not use layers,
        # which means the Products code is not loaded,
        # so we need to import it explicitly.
        # This is done once.
        try:
            from Products.isurlinportal import isURLInPortal
        except ImportError:
            # If this somehow fails, it seems better to have a safe fallback,
            # instead of a hard failure.
            return False

        return isURLInPortal(self, url, context=context)


URLTool.__doc__ = BaseTool.__doc__

InitializeClass(URLTool)
