from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFPlone import ToolNames
from Products.CMFPlone.interfaces.PloneBaseTool import IPloneBaseTool

class PloneBaseTool:
    """Base class of all tools used in CMFPlone and Plone Core
    """
    
    security = ClassSecurityInfo()
    
    __implements__ = IPloneBaseTool

InitializeClass(PloneBaseTool)
