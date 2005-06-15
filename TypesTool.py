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
        Overriding listTypeInfo from CMFCore.TypesTool.  The original method was
        doing security checks on the TypeInformation objects themselves in
        addtion to the isConstructionAllowed test.  This was very expensive and
        only useful if someone had set custom security restrictions on some
        TypeInformation objects in the types tool through the ZMI.  I cannot see
        a reasonable reason for someone to do such a thing.  Also, removed a
        check for null TypeInfo.getId(), as this will never happen, if it
        does it's a bug in and of itself and shouldn't be ignored.  Also,
        changed the check shich ensures that our objectValues() are TypeInfoish
        to use the clear and sane interface.isImplementedBy(obj) instead of the
        getattr(aq_base(type),'_isTypeInformation',0) it was using before.
        ~alecm
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
