from Products.CMFCore.PortalContent import PortalContent
from Products.CMFPlone.utils import log_deprecated
from Globals import InitializeClass

class PloneContent(PortalContent):
    # BBB To be removed in Plone 4.0
    log_deprecated("PloneContent is deprecated and will be removed in Plone "
                   "4.0. Use (marker) interfaces instead to get a way to check "
                   "for a functionality that is common to some types.")

PloneContent.__doc__ = PortalContent.__doc__

InitializeClass(PloneContent)
