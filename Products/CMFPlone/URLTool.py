from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl.class_init import InitializeClass
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.URLTool import URLTool as BaseTool
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.patches.gtbn import rewrap_in_request_container
from zope.component import getUtility


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

    def getPortalObject(self):
        portal = aq_parent(aq_inner(self))
        if portal is None:
            portal = getUtility(ISiteRoot)
        # Make sure portal can acquire REQUEST
        return rewrap_in_request_container(portal, context=self)


URLTool.__doc__ = BaseTool.__doc__

InitializeClass(URLTool)
