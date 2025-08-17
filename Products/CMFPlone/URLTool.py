from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.URLTool import URLTool as BaseTool
from Products.CMFPlone.patches.gtbn import rewrap_in_request_container
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.isurlinportal import isURLInPortal
from zope.component import getUtility


class URLTool(PloneBaseTool, BaseTool):
    meta_type = "Plone URL Tool"
    security = ClassSecurityInfo()
    toolicon = "skins/plone_images/link_icon.png"

    # The implementation of this method was moved to Products.isurlinportal
    # to be able to more quickly do a security release in case there is a
    # problem in this part.
    isURLInPortal = isURLInPortal

    def getPortalObject(self):
        portal = aq_parent(aq_inner(self))
        if portal is None:
            portal = getUtility(ISiteRoot)
        # Make sure portal can acquire REQUEST
        return rewrap_in_request_container(portal, context=self)


URLTool.__doc__ = BaseTool.__doc__

InitializeClass(URLTool)
