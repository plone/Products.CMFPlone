import sys
import urllib
from Globals import InitializeClass
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent, aq_base, aq_inner, aq_chain, aq_get
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem
from ZPublisher.Publish import call_object, missing_name, dont_publish_class
from ZPublisher.mapply import mapply
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.Skinnable import SkinnableObjectManager
from Products.CMFPlone.PloneFolder import PloneFolder as TempFolderBase


# ##############################################################################
# A class used for generating the temporary folder that will
# hold temporary objects.  We need a separate class so that
# we can add all types to types_tool's allowed_content_types
# for the class without having side effects in the rest of
# the portal.
class TempFolder(TempFolderBase):
    portal_type = meta_type = 'TempFolder'
    isPrincipiaFolderish = 0

    parent = None

    def __getitem__(self, id):
        if id in self.objectIds():
            return self._getOb(id).__of__(aq_parent(aq_parent(self)))
        else:
            type_name = self.getId()
            self.invokeFactory(id=id, type_name=type_name)
            obj = self._getOb(id).__of__(aq_parent(aq_parent(self)))
            obj.unindexObject()
            return obj

#    def __ac_local_roles__(self):
#        membership_tool = getToolByName(self, 'portal_membership')
#        member = membership_tool.getAuthenticatedMember()
#        return {member.getUserName():['Owner']}



# ##############################################################################
class FactoryTool(UniqueObject, SimpleItem):
    """ """
    id = 'portal_factory'
    meta_type= 'Plone Factory Tool'
    security = ClassSecurityInfo()
    isPrincipiaFolderish = 0

    manage_options = ( ({'label':'Overview', 'action':'manage_overview'},) +
                       SimpleItem.manage_options)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('www/portal_factory_manage_overview', globals())
    manage_overview.__name__ = 'manage_overview'
    manage_overview._need__name__ = 0

    manage_main = manage_overview

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
            folder = aq_parent(aq_parent(aq_parent(aq_inner(obj))))
            folder.invokeFactory(id=id, type_name=type_name)
            obj = getattr(folder, id)

            # give ownership to currently authenticated member if not anonymous
            membership_tool = getToolByName(self, 'portal_membership')
            if not membership_tool.isAnonymousUser():
                member = membership_tool.getAuthenticatedMember()
                obj.changeOwnership(member.getUser(), 1)
                obj.manage_setLocalRoles(member.getUserName(), ['Owner'])

            return obj


    def fixRequest(self):
        """Our before_publishing_traverse call mangles URL0.  This fixes up
        the REQUEST."""
        factory_info = self.REQUEST.get('__factory_info__', {})
        stack = factory_info.get('stack',[])
        if stack:
            URL = self.REQUEST.URL0 + '/' + '/'.join(stack)
        else:
            URL = self.REQUEST.URL0

        self.REQUEST.set('URL', URL)

        url_list = URL.split('/')
        n = 0
        while len(url_list) > 0 and url_list[-1] != '':
            self.REQUEST.set('URL%d' % n, '/'.join(url_list))
            url_list = url_list[:-1]
            n = n + 1

        url_list = URL.split('/')
        m = 0
        while m < n:
            self.REQUEST.set('BASE%d' % m, '/'.join(url_list[0:len(url_list)-n+1+m]))
            m = m + 1
        # XXX fix URLPATHn here too


    def isTemporary(self, obj):
        """Check to see if an object is temporary"""
        ob = aq_parent(aq_inner(obj))
        return hasattr(ob, 'meta_type') and ob.meta_type == TempFolder.meta_type


    def __before_publishing_traverse__(self, other, REQUEST):
        # prevent further traversal
        stack = REQUEST.get('TraversalRequestNameStack')
        stack.reverse()
        REQUEST.set('TraversalRequestNameStack', [])
        factory_info = {'stack':stack}
        REQUEST.set('__factory_info__', factory_info)


    security.declarePublic('__call__')
    def __call__(self, *args, **kwargs):
        """call method"""

        factory_info = self.REQUEST.get('__factory_info__', {})
        if not factory_info.get('fixed_request'):
            self.fixRequest()
            factory_info['fixed_request'] = 1
            self.REQUEST.set('__factory_info__', factory_info)

        stack = factory_info['stack']
        # stack.reverse()
        if len(stack) < 2:
            obj = self.restrictedTraverse('/'.join(stack))
            if args == ():
                # XXX hideous hack -- why isn't REQUEST passed in in args??
                args = (self.REQUEST, )
            return mapply(obj, self.REQUEST.args, self.REQUEST,
                               call_object, 1, missing_name, dont_publish_class,
                               self.REQUEST, bind=1)
        id = stack[1]
        if id in aq_parent(self).objectIds():
            return aq_parent(self).restrictedTraverse('/'.join(stack[1:]))(*args, **kwargs)

        tempFolder = self.getTempFolder(stack[0])

        path = '/'.join(stack[1:])
        obj = tempFolder.restrictedTraverse(path)
        
        return mapply(obj, self.REQUEST.args, self.REQUEST,
                               call_object, 1, missing_name, dont_publish_class,
                               self.REQUEST, bind=1)


    index_html = None  # call __call__, not index_html


    def getTempFolder(self, type_name):
        factory_info = self.REQUEST.get('__factory_info__', {})
        tempFolder = factory_info.get('tempFolder', None)
        if not tempFolder:
            type_name = urllib.unquote(type_name)
            # make sure we can add an object of this type to the temp folder
            types_tool = getToolByName(self, 'portal_types')
            if not type_name in types_tool.listContentTypes():
                raise ValueError, 'Unrecognized type %s\n' % type_name
            if not type_name in types_tool.TempFolder.allowed_content_types:
                # update allowed types for tempfolder
                types_tool.TempFolder.allowed_content_types=(types_tool.listContentTypes())

            tempFolder = TempFolder(type_name)
            tempFolder.parent = aq_parent(self)
            tempFolder = aq_inner(tempFolder).__of__(self)
            tempFolder.manage_permission(CMFCorePermissions.AddPortalContent, ('Anonymous','Authenticated',), acquire=0 )
            tempFolder.manage_permission(CMFCorePermissions.ModifyPortalContent, ('Anonymous','Authenticated',), acquire=0 )
            tempFolder.manage_permission('Copy or Move', ('Anonymous','Authenticated',), acquire=0 )
        else:
            tempFolder = aq_inner(tempFolder).__of__(self)
        factory_info['tempFolder'] = tempFolder
        self.REQUEST.set('__factory_info__', factory_info)
        return tempFolder



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

        # unmangle type name
        type_name = urllib.unquote(name)
        types_tool = getToolByName(self, 'portal_types')
        # make sure this is really a type name
        if not type_name in types_tool.listContentTypes():
            # nope -- do nothing
            return getattr(self, name)
        return self.getTempFolder(name)

InitializeClass(FactoryTool)
