import logging
import os

from zope.interface import implements
from zope.structuredtext import stx2html

from AccessControl import Owned, ClassSecurityInfo, getSecurityManager
from Acquisition import aq_parent, aq_base, aq_inner, aq_get
from App.class_init import InitializeClass
from App.Common import package_home
from OFS.SimpleItem import SimpleItem
from ZPublisher.Publish import call_object, missing_name, dont_publish_class
from ZPublisher.mapply import mapply
from Products.CMFPlone import cmfplone_globals
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IFactoryTool
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from Products.CMFPlone.PloneFolder import PloneFolder as TempFolderBase
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import log_exc
from ZODB.POSException import ConflictError

FACTORY_INFO = '__factory__info__'


class FauxArchetypeTool(object):
    """A faux archetypes tool which prevents content from being indexed."""

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, tool):
        self.tool = tool

    def getCatalogsByType(self, type_name):
        return []

    def __getitem__(self, id):
        return getattr(self.tool, id)


def _createObjectByType(type_name, container, id, *args, **kw):
    """This function replaces Products.CMFPlone.utils._createObjectByType.

    If no product is set on fti, use IFactory to lookup the factory.
    Additionally we add 'container' as 'parent' kw argument when calling the
    IFactory implementation. this ensures the availability of the acquisition
    chain if needed inside the construction logic.

    The kw argument hack is some kind of semi-valid since the IFactory interface
    promises the __call__ function to accept all given args and kw args.
    As long as the specific IFactory implementation provides this signature
    everything works well unless any other 3rd party factory expects another
    kind of object as 'parent' kw arg than the provided one.
    """
    id = str(id)
    typesTool = getToolByName(container, 'portal_types')
    fti = typesTool.getTypeInfo(type_name)
    if not fti:
        raise ValueError, 'Invalid type %s' % type_name

    if not fti.product:
        kw['parent'] = container

    return fti._constructInstance(container, id, *args, **kw)


# ##############################################################################
# A class used for generating the temporary folder that will
# hold temporary objects.  We need a separate class so that
# we can add all types to types_tool's allowed_content_types
# for the class without having side effects in the rest of
# the portal.
class TempFolder(TempFolderBase):

    portal_type = meta_type = 'TempFolder'
    isPrincipiaFolderish = 0

    implements(IHideFromBreadcrumbs)

    # override getPhysicalPath so that temporary objects return a full path
    # that includes the acquisition parent of portal_factory (otherwise we get
    # portal_root/portal_factory/... no matter where the object will reside)
    def getPhysicalPath(self):
        '''Returns a path (an immutable sequence of strings)
        that can be used to access this object again
        later, for example in a copy/paste operation.  getPhysicalRoot()
        and getPhysicalPath() are designed to operate together.
        '''
        portal_factory = aq_parent(aq_inner(self))
        path = aq_parent(portal_factory).getPhysicalPath() + \
            (portal_factory.getId(), self.getId(), )
        return path

    # override / delegate local roles methods
    def __ac_local_roles__(self):
        """__ac_local_roles__ needs to be handled carefully.
        Zope's and GRUF's User.getRolesInContext both walk up the
        acquisition hierarchy using aq_parent(aq_inner(obj)) when
        they gather local roles, and this process will result in
        their walking from TempFolder to portal_factory to the portal root."""
        object = aq_parent(aq_parent(self))
        local_roles = {}
        while 1:
            # Get local roles for this user
            lr = getattr(object, '__ac_local_roles__', None)
            if lr:
                if callable(lr):
                    lr=lr()
                lr = lr or {}
                for k, v in lr.items():
                    if not k in local_roles:
                        local_roles[k] = []
                    for role in v:
                        if not role in local_roles[k]:
                            local_roles[k].append(role)

            # Check if local role has to be acquired (PLIP 16)
            if getattr(object, '__ac_local_roles_block__', None):
                # Ok, we have to stop there, as lr. blocking is enabled
                break

            # Prepare next iteration
            inner = getattr(object, 'aq_inner', object)
            parent = getattr(inner, 'aq_parent', None)
            if parent is not None:
                object = parent
                continue
            if hasattr(object, 'im_self'):
                object=object.im_self
                object=getattr(object, 'aq_inner', object)
                continue
            break
        return local_roles

    def has_local_roles(self):
        return len(self.__ac_local_roles__())

    def get_local_roles_for_userid(self, userid):
        return tuple(self.__ac_local_roles__().get(userid, []))

    def get_valid_userids(self):
        return aq_parent(aq_parent(self)).get_valid_userids()

    def valid_roles(self):
        return aq_parent(aq_parent(self)).valid_roles()

    def validate_roles(self, roles):
        return aq_parent(aq_parent(self)).validate_roles(roles)

    def userdefined_roles(self):
        return aq_parent(aq_parent(self)).userdefined_roles()

    # delegate Owned methods
    def owner_info(self):
        return aq_parent(aq_parent(self)).owner_info()

    def getOwner(self, info=0,
                 aq_get=aq_get,
                 UnownableOwner=Owned.UnownableOwner,
                 getSecurityManager=getSecurityManager,
                 ):
        return aq_parent(aq_parent(self)).getOwner(info, aq_get, UnownableOwner, getSecurityManager)

    def userCanTakeOwnership(self):
        return aq_parent(aq_parent(self)).userCanTakeOwnership()

    # delegate allowedContentTypes
    def allowedContentTypes(self):
        return aq_parent(aq_parent(self)).allowedContentTypes()

    def __getitem__(self, id):
        # Zope's inner acquisition chain for objects returned by __getitem__ will be
        # portal -> portal_factory -> temporary_folder -> object
        # What we really want is for the inner acquisition chain to be
        # intended_parent_folder -> portal_factory -> temporary_folder -> object
        # So we need to rewrap...
        portal_factory = aq_parent(aq_inner(self))
        intended_parent = aq_parent(portal_factory)

        # If the intended parent has an object with the given id, just do a passthrough
        if hasattr(intended_parent, id):
            return getattr(intended_parent, id)

        # rewrap portal_factory
        portal_factory = aq_base(portal_factory).__of__(intended_parent)
        # rewrap self
        temp_folder = aq_base(self).__of__(portal_factory)

        if id in self:
            return (aq_base(self._getOb(id)).__of__(temp_folder)).__of__(intended_parent)
        else:
            type_name = self.getId()
            try:
                # We fake an archetype tool which returns no catalogs for the
                # object to be indexed in to avoid it showing up in the catalog
                # in the first place.
                self.archetype_tool = FauxArchetypeTool(getToolByName(self, 'archetype_tool'))
                _createObjectByType(type_name, self, id)
            except ConflictError:
                raise
            except:
                # some errors from invokeFactory (AttributeError, maybe others)
                # get swallowed -- dump the exception to the log to make sure
                # developers can see what's going on
                log_exc(severity=logging.DEBUG)
                raise
            obj = self._getOb(id)

            # keep obj out of the catalog
            obj.unindexObject()

            # additionally keep it out of Archetypes UID and refs catalogs
            if base_hasattr(obj, '_uncatalogUID'):
                obj._uncatalogUID(obj)
            if base_hasattr(obj, '_uncatalogRefs'):
                obj._uncatalogRefs(obj)

            return (aq_base(obj).__of__(temp_folder)).__of__(intended_parent)

    # ignore rename requests since they don't do anything
    def manage_renameObject(self, id, new_id, REQUEST=None):
        pass


# ##############################################################################
class FactoryTool(PloneBaseTool, UniqueObject, SimpleItem):
    """ """
    id = 'portal_factory'
    meta_type= 'Plone Factory Tool'
    toolicon = 'skins/plone_images/add_icon.png'
    security = ClassSecurityInfo()
    isPrincipiaFolderish = 0

    implements(IFactoryTool, IHideFromBreadcrumbs)

    manage_options = (({'label': 'Overview', 'action': 'manage_overview'}, \
                       {'label': 'Documentation', 'action': 'manage_docs'}, \
                       {'label': 'Factory Types', 'action': 'manage_portal_factory_types'},) +
                      SimpleItem.manage_options)

    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('www/portal_factory_manage_overview', globals())
    manage_overview.__name__ = 'manage_overview'
    manage_overview._need__name__ = 0

    security.declareProtected(ManagePortal, 'manage_portal_factory_types')
    manage_portal_factory_types = PageTemplateFile(os.path.join('www', 'portal_factory_manage_types'), globals())
    manage_portal_factory_types.__name__ = 'manage_portal_factory_types'
    manage_portal_factory_types._need__name__ = 0

    manage_main = manage_overview

    security.declareProtected(ManagePortal, 'manage_docs')
    manage_docs = PageTemplateFile(os.path.join('www', 'portal_factory_manage_docs'), globals())
    manage_docs.__name__ = 'manage_docs'

    wwwpath = os.path.join(package_home(cmfplone_globals), 'www')
    f = open(os.path.join(wwwpath, 'portal_factory_docs.stx'), 'r')
    _docs = f.read()
    f.close()
    _docs = stx2html(_docs)

    security.declarePublic('docs')
    def docs(self):
        """Returns FactoryTool docs formatted as HTML"""
        return self._docs

    def getFactoryTypes(self):
        if not hasattr(self, '_factory_types'):
            self._factory_types = {}
        return self._factory_types

    security.declareProtected(ManagePortal, 'manage_setPortalFactoryTypes')
    def manage_setPortalFactoryTypes(self, REQUEST=None, listOfTypeIds=None):
        """Set the portal types that should use the factory."""
        if listOfTypeIds is not None:
            dict = {}
            for l in listOfTypeIds:
                dict[l] = 1
        elif REQUEST is not None:
            dict = REQUEST.form
        if dict is None:
            dict = {}
        self._factory_types = {}
        types_tool = getToolByName(self, 'portal_types')
        for t in types_tool.listContentTypes():
            if t in dict:
                self._factory_types[t] = 1
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_main')

    def doCreate(self, obj, id=None, **kw):
        """Create a real object from a temporary object."""
        if self.isTemporary(obj=obj):
            if id is not None:
                id = id.strip()
            if not id:
                if hasattr(obj, 'getId') and callable(getattr(obj, 'getId')):
                    id = obj.getId()
                else:
                    id = getattr(obj, 'id', None)
            type_name = aq_parent(aq_inner(obj)).id  # get the ID of the TempFolder
            folder = aq_parent(aq_parent(aq_parent(aq_inner(obj))))
            folder.invokeFactory(id=id, type_name=type_name)
            obj = getattr(folder, id)

            # give ownership to currently authenticated member if not anonymous
            # TODO is this necessary?
            membership_tool = getToolByName(self, 'portal_membership')
            if not membership_tool.isAnonymousUser():
                member = membership_tool.getAuthenticatedMember()
                obj.changeOwnership(member.getUser(), 1)
            if hasattr(aq_base(obj), 'manage_afterPortalFactoryCreate'):
                obj.manage_afterPortalFactoryCreate()
        return obj

    def _fixRequest(self):
        """Our before_publishing_traverse call mangles URL0.  This fixes up
        the REQUEST."""
        # Everything seems to work without this method being called at all...
        factory_info = self.REQUEST.get(FACTORY_INFO, None)
        if not factory_info:
            return
        stack = factory_info['stack']
        FACTORY_URL = self.REQUEST.URL
        URL = '/'.join([FACTORY_URL] + stack)
        self.REQUEST.set('URL', URL)

        url_list = URL.split('/')
        n = 0
        while len(url_list) > 0 and url_list[-1] != '':
            self.REQUEST.set('URL%d' % n, '/'.join(url_list))
            url_list = url_list[:-1]
            n = n + 1

        # BASE1 is the url of the Zope App object
        n = len(self.REQUEST._steps) + 2
        base = FACTORY_URL
        for part in stack:
            base = '%s/%s' % (base, part)
            self.REQUEST.set('BASE%d' % n, base)
            n += 1
        # TODO fix URLPATHn, BASEPATHn here too

    def isTemporary(self, obj):
        """Check to see if an object is temporary"""
        ob = aq_base(aq_parent(aq_inner(obj)))
        return hasattr(ob, 'meta_type') and ob.meta_type == TempFolder.meta_type

    def __before_publishing_traverse__(self, other, REQUEST):

        if REQUEST.get(FACTORY_INFO, None):
            del REQUEST[FACTORY_INFO]

        stack = REQUEST.get('TraversalRequestNameStack')
        stack = [str(s) for s in stack]  # convert from unicode if necessary (happens in Epoz for some weird reason)
        # need 2 more things on the stack at least for portal_factory to kick in:
        #    (1) a type, and (2) an id
        if len(stack) < 2: # ignore
            return

        # Keep track of how many path elements we want to eat
        gobbled_length = 0

        type_name = stack[-1]
        types_tool = getToolByName(self, 'portal_types')
        # make sure this is really a type name
        if not type_name in types_tool.listContentTypes():
            return # nope -- do nothing

        gobbled_length += 1

        id = stack[-2]
        intended_parent = aq_parent(self)
        if hasattr(intended_parent, id):
            return # do normal traversal via __bobo_traverse__

        gobbled_length += 1

        # about to create an object

        # before halting traversal, check for method aliases
        # stack should be [...optional stuff..., id, type_name]
        key = len(stack) >= 3 and stack[-3] or '(Default)'
        ti = types_tool.getTypeInfo(type_name)
        method_id = ti and ti.queryMethodID(key)
        if method_id:
            if key != '(Default)':
                del(stack[-3])
            if method_id != '(Default)':
                stack.insert(-2, method_id)
                gobbled_length += 1
            REQUEST._hacked_path = 1
        else:
            gobbled_length += 1

        # Pevent further traversal if we are doing a normal factory request,
        # but allow it if there is a traversal sub-path beyond the (edit)
        # view on the content item. In this case, portal_factory will not
        # be responsible for rendering the object.
        if len(stack) <= gobbled_length:
            REQUEST.set('TraversalRequestNameStack', [])

        stack.reverse()
        factory_info = {'stack': stack}
        REQUEST.set(FACTORY_INFO, factory_info)

    def __bobo_traverse__(self, REQUEST, name):
        # __bobo_traverse__ can be invoked directly by a restricted_traverse method call
        # in which case the traversal stack will not have been cleared by __before_publishing_traverse__
        name = str(name) # fix unicode weirdness
        types_tool = getToolByName(self, 'portal_types')
        if not name in types_tool.listContentTypes():
            return getattr(self, name) # not a type name -- do the standard thing
        return self._getTempFolder(str(name)) # a type name -- return a temp folder

    security.declarePublic('__call__')
    def __call__(self, *args, **kwargs):
        """call method"""
        self._fixRequest()
        factory_info = self.REQUEST.get(FACTORY_INFO, {})
        stack = factory_info['stack']
        type_name = stack[0]
        id = stack[1]

        # do a passthrough if parent contains the id
        if id in aq_parent(self):
            return aq_parent(self).restrictedTraverse('/'.join(stack[1:]))(*args, **kwargs)

        tempFolder = self._getTempFolder(type_name)
        # Mysterious hack that fixes some problematic interactions with SpeedPack:
        #   Get the first item in the stack by explicitly calling __getitem__
        temp_obj = tempFolder.__getitem__(id)
        stack = stack[2:]
        if stack:
            obj = temp_obj.restrictedTraverse('/'.join(stack))

            # Mimic URL traversal, sort of
            if getattr(aq_base(obj), 'index_html', None):
                obj = obj.restrictedTraverse('index_html')
            else:
                obj = getattr(obj, 'GET', obj)

        else:
            obj = temp_obj
        return mapply(obj, self.REQUEST.args, self.REQUEST,
                               call_object, 1, missing_name, dont_publish_class,
                               self.REQUEST, bind=1)

    index_html = None  # call __call__, not index_html

    def _getTempFolder(self, type_name):
        factory_info = self.REQUEST.get(FACTORY_INFO, {})
        tempFolder = factory_info.get(type_name, None)
        if tempFolder is not None:
            tempFolder = aq_inner(tempFolder).__of__(self)
            return tempFolder

        # make sure we can add an object of this type to the temp folder
        types_tool = getToolByName(self, 'portal_types')
        if not type_name in types_tool.TempFolder.allowed_content_types:
            # update allowed types for tempfolder
            types_tool.TempFolder.allowed_content_types=(types_tool.listContentTypes())

        tempFolder = TempFolder(type_name).__of__(self)

        factory_info[type_name] = tempFolder
        self.REQUEST.set(FACTORY_INFO, factory_info)
        return tempFolder

InitializeClass(FactoryTool)
