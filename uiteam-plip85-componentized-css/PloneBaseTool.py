from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.interfaces.PloneBaseTool import IPloneBaseTool

class PloneBaseTool:
    """Base class of all tools used in CMFPlone and Plone Core
    """
    
    security = ClassSecurityInfo()
    
    __implements__ = IPloneBaseTool

InitializeClass(PloneBaseTool)
