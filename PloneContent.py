from Products.CMFCore.PortalContent import PortalContent
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class PloneContent(PortalContent):
    pass

PloneContent.__doc__ = PortalContent.__doc__

InitializeClass(PloneContent)
