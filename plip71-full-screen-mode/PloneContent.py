from Products.CMFCore.PortalContent import PortalContent
from Globals import InitializeClass

class PloneContent(PortalContent):
    pass

PloneContent.__doc__ = PortalContent.__doc__

InitializeClass(PloneContent)
