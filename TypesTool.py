from Products.CMFCore.TypesTool import TypesTool as BaseTool
from Products.CMFCore.interfaces.portal_types import ContentTypeInformation
from Products.CMFCore.CMFCorePermissions import AccessContentsInformation
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class TypesTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.TypesTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/document_icon.gif'
    
    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

    security.declarePublic('listTypeTitles')
    def listTypeTitles(self, container=None):
        """ Return a dictionary of id/Title combinations """
        typenames = {}
        for t in self.listTypeInfo( container ):
            name = t.getId()
            if name:
                typenames[ name ] = t.title_or_id()

        return typenames

    security.declareProtected(AccessContentsInformation, 'listTypeInfo')
    def listTypeInfo( self, container=None ):
        """
            Remove silly security and getId checks from the CMFCore method
        """
        rval = []
        for t in self.objectValues():
            # Filter out things that aren't TypeInformation and
            # types for which the user does not have adequate permission.
            if not ContentTypeInformation.isImplementedBy(t):
                continue
            if container is not None:
                if not t.isConstructionAllowed(container):
                    continue
            rval.append(t)
        return rval

TypesTool.__doc__ = BaseTool.__doc__

InitializeClass(TypesTool)
