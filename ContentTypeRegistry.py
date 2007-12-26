from Globals import InitializeClass
from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import access_contents_information

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.ContentTypeRegistry import ContentTypeRegistry as BaseTool

from Products.CMFPlone import ToolNames
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class DelegatingContentTypeRegistry(PloneBaseTool, BaseTool):
    """Implements a content type registry that can delegate to another
    one higher up in the acquisition hierarchy.
    """

    meta_type = ToolNames.DelegatingContentTypeRegistry
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/contentrules_icon.gif'

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

    security.declareProtected(access_contents_information, 'findTypeName')
    def findTypeName(self, name, typ, body):
        """ Perform a lookup over a collection of rules, returning the
        the name of the Type object corresponding to name/typ/body.

        If no match is found in the local tool, look up higher in the
        hierarchy.

        Return None if no match found.
        """
        typeName = BaseTool.findTypeName(self, name, typ, body)
        if typeName is not None:
            return typeName
        parent = aq_parent(aq_inner(aq_parent(aq_inner(self))))
        tool = getToolByName(parent, self.id, None)
        if tool is not None:
            return tool.findTypeName(name, typ, body)                

InitializeClass(DelegatingContentTypeRegistry)
