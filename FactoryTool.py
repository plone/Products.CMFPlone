from Products.CMFCore.utils import UniqueObject, getToolByName                        
from Globals import InitializeClass
from Acquisition import aq_parent, aq_base, aq_inner, aq_chain 
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from DateTime import DateTime
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.PortalFolder import PortalFolder
from DateTime import DateTime
import urllib
import sys

# ##############################################################################
# A class used for generating the temporary folder that will
# hold temporary objects.  We need a separate class so that
# we can add all types to types_tool's allowed_content_types
# for the class without having side effects in the rest of
# the portal.
class TempFolder(PortalFolder):
    portal_type = meta_type = 'TempFolder'

    def __getitem__(self, id):
        # see if the object exists in the parent context
        if hasattr(aq_parent(self), id):
            # if so, just do a pass-through
            return getattr(self.getParentNode(), id)
#        elif hasattr(self, id):
#            return self._getOb(id)
        else:
            type_name = self.getId()
            type_name = urllib.unquote(type_name)
            # make sure we can add an object of this type to the temp folder
            types_tool = getToolByName(self, 'portal_types')
            if not type_name in types_tool.TempFolder.allowed_content_types:
                # update allowed types for tempfolder
                types_tool.TempFolder.allowed_content_types=(types_tool.listContentTypes())
            self.invokeFactory(id=id, type_name=type_name)
            obj = self._getOb(id).__of__(aq_parent(aq_parent(self)))

            # give ownership to currently authenticated member if not anonymous
            membership_tool = getToolByName(self, 'portal_membership')
            if not membership_tool.isAnonymousUser():
                member = membership_tool.getAuthenticatedMember()
                obj.changeOwnership(member.getUser(), 1)
                obj.manage_setLocalRoles(member.getUserName(), ['Owner'])

            obj.unindexObject()
            return obj

# ##############################################################################
class FactoryTool(UniqueObject, SimpleItem):
    """ """
    id = 'portal_factory'
    meta_type= 'Plone Factory Tool'
    security = ClassSecurityInfo()

    def doCreate(self, obj, id=None, **kw):
        """Create a real object from a temporary object."""
        if not self.isTemporary(obj=obj):
            return obj
        else:
            if id is not None:
                id = id.strip()
            if hasattr(obj, 'getId') and callable(getattr(obj, 'getId')):
                obj_id = obj.getId()
            else:
                obj_id = getattr(id, 'id', None)
            if obj_id is None:
                raise Exception  # XXX - FIXME
            if not id:
                id = obj_id
            type_name = aq_parent(aq_inner(obj)).id
            folder = aq_parent(aq_parent(aq_inner(obj)))
            folder.invokeFactory(id=id, type_name=type_name)
            obj = getattr(folder, id)

            # give ownership to currently authenticated member if not anonymous
            membership_tool = getToolByName(self, 'portal_membership')
            if not membership_tool.isAnonymousUser():
                member = membership_tool.getAuthenticatedMember()
                obj.changeOwnership(member.getUser(), 1)
                obj.manage_setLocalRoles(member.getUserName(), ['Owner'])

            return obj


    def isTemporary(self, obj):
        """Check to see if an object is temporary"""
        return aq_parent(aq_inner(obj)).meta_type == TempFolder.meta_type


    def __bobo_traverse__(self, REQUEST, name):
        """ """
        # The portal factory intercepts URLs of the form
        #   .../portal_factory/TYPE_NAME/ID/...
        # where TYPE_NAME is a type from portal_types.listContentTypes() and
        # ID is the desired ID for the object.  For intercepted URLs, 
        # portal_factory creates a temporary object of type TYPE_NAME with
        # id ID and puts it on the traversal stack.  The context for the
        # temporary object is set to portal_factory's context.
        #
        # If the object with id ID already exists in portal_factory's context,
        # portal_factory returns the existing object.
        #
        # All other requests are passed through unchanged.
        # 

        # try to extract a type string from next piece of the URL
        encoded_type_name = name
        # unmangle type name
        type_name = urllib.unquote(encoded_type_name)
        types_tool = getToolByName(self, 'portal_types')
        # make sure this is really a type name
        if not type_name in types_tool.listContentTypes():
            # nope -- do nothing
            return getattr(self, name)
        # create a temporary object
#        tempFolder = TempFolder(encoded_type_name).__of__(aq_parent(self))
        tempFolder = TempFolder(encoded_type_name).__of__(self)
        # modify permissions to allow people to add, modify, and copy/move/rename temporary objects
        tempFolder.manage_permission(CMFCorePermissions.AddPortalContent, ('Anonymous','Authenticated',), acquire=1 )
        tempFolder.manage_permission(CMFCorePermissions.ModifyPortalContent, ('Anonymous','Authenticated',), acquire=1 )
        tempFolder.manage_permission('Copy or Move', ('Anonymous','Authenticated',), acquire=1 )
        tempFolder.unindexObject()
        
        return tempFolder.__of__(aq_parent(self))

InitializeClass(FactoryTool)