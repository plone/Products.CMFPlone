from types import StringType
from Globals import InitializeClass
from zExceptions import NotFound
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl import Permissions
from AccessControl import Unauthorized
from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute

from OFS.Folder import Folder
from OFS.ObjectManager import REPLACEABLE
from DocumentTemplate.sequence import sort
from webdav.NullResource import NullResource
from webdav.WriteLockInterface import WriteLockInterface
from webdav.interfaces import IWriteLock

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFCore.permissions import AccessContentsInformation, \
                    AddPortalContent, AddPortalFolders, ListFolderContents, \
                    ManageProperties, ModifyPortalContent, View
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from zope.interface import implements
from zope.app.container.contained import notifyContainerModified

# ATM it's safer to define our own
from interfaces.OrderedContainer import IOrderedContainer
from OFS.IOrderSupport import IOrderedContainer as IZopeOrderedContainer

class ReplaceableWrapper:
    """A wrapper around an object to make it replaceable."""
    def __init__(self, ob):
        self.__ob = ob

    def __getattr__(self, name):
        if name == '__replaceable__':
            return REPLACEABLE
        return getattr(self.__ob, name)

# Portions of this class was copy/pasted from the OFS.Folder.OrderedFolder
# from Zope2.7.  This class is licensed under the ZPL 2.0 as stated here:
# http://www.zope.org/Resources/ZPL
# Zope Public License (ZPL) Version 2.0
# This software is Copyright (c) Zope Corporation (tm) and Contributors.
# All rights reserved.

class OrderedContainer(Folder):
    """Folder with subobject ordering support."""

    security = ClassSecurityInfo()

    security.declareProtected(ModifyPortalContent, 'moveObject')
    def moveObject(self, id, position):
        obj_idx  = self.getObjectPosition(id)
        if obj_idx == position:
            return None
        elif position < 0:
            position = 0

        metadata = list(self._objects)
        obj_meta = metadata.pop(obj_idx)
        metadata.insert(position, obj_meta)
        self._objects = tuple(metadata)

    # Here the implementation of IOrderedContainer starts
    # Once Plone depends on Zope 2.7 this should be replaced by mixing in
    # the 2.7 specific class OFS.OrderedContainer.OrderedContainer

    security.declareProtected(ModifyPortalContent, 'moveObjectsByDelta')
    def moveObjectsByDelta(self, ids, delta, subset_ids=None,
                           suppress_events=False):
        """Move specified sub-objects by delta."""
        if type(ids) is StringType:
            ids = (ids,)
        min_position = 0
        objects = list(self._objects)
        if subset_ids == None:
            subset_ids = self.getCMFObjectsSubsetIds(objects)
        else:
            subset_ids = list(subset_ids)
        # unify moving direction
        if delta > 0:
            ids = list(ids)
            ids.reverse()
            subset_ids.reverse()
        counter = 0

        for id in ids:
            try:
                old_position = subset_ids.index(id)
            except ValueError:
                continue
            new_position = max(old_position - abs(delta), min_position)
            if new_position == min_position:
                min_position += 1
            if not old_position == new_position:
                subset_ids.remove(id)
                subset_ids.insert(new_position, id)
                counter += 1

        if counter > 0:
            if delta > 0:
                subset_ids.reverse()
            obj_dict = {}
            for obj in objects:
                obj_dict[obj['id']] = obj
            pos = 0
            for i in range(len(objects)):
                if objects[i]['id'] in subset_ids:
                    try:
                        objects[i] = obj_dict[subset_ids[pos]]
                        pos += 1
                    except KeyError:
                        raise ValueError('The object with the id "%s" does '
                                         'not exist.' % subset_ids[pos])
            self._objects = tuple(objects)

        if not suppress_events:
            notifyContainerModified(self)

        return counter

    security.declarePrivate('getCMFObjectsSubsetIds')
    def getCMFObjectsSubsetIds(self, objs):
        """Get the ids of only cmf objects (used for moveObjectsByDelta)."""
        ttool = getToolByName(self, 'portal_types')
        cmf_meta_types = [ti.Metatype() for ti in ttool.listTypeInfo()]
        return [obj['id'] for obj in objs if obj['meta_type'] in cmf_meta_types]

    security.declareProtected(ModifyPortalContent, 'getObjectPosition')
    def getObjectPosition(self, id):

        objs = list(self._objects)
        om = [objs.index(om) for om in objs if om['id']==id]

        if om: # only 1 in list if any
            return om[0]

        raise NotFound, 'Object %s was not found' % str(id)

    security.declareProtected(ModifyPortalContent, 'moveObjectsUp')
    def moveObjectsUp(self, ids, delta=1, RESPONSE=None):
        """Move an object up."""
        self.moveObjectsByDelta(ids, -delta)
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(ModifyPortalContent, 'moveObjectsDown')
    def moveObjectsDown(self, ids, delta=1, RESPONSE=None):
        """Move an object down."""
        self.moveObjectsByDelta(ids, delta)
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(ModifyPortalContent, 'moveObjectsToTop')
    def moveObjectsToTop(self, ids, RESPONSE=None):
        """Move an object to the top."""
        self.moveObjectsByDelta(ids, - len(self._objects))
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(ModifyPortalContent, 'moveObjectsToBottom')
    def moveObjectsToBottom(self, ids, RESPONSE=None):
        """Move an object to the bottom."""
        self.moveObjectsByDelta(ids, len(self._objects))
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    security.declareProtected(ModifyPortalContent, 'moveObjectToPosition')
    def moveObjectToPosition(self, id, position, suppress_events=False):
        """Move specified object to absolute position."""
        delta = position - self.getObjectPosition(id)
        return self.moveObjectsByDelta(id, delta,
                                       suppress_events=suppress_events)

    security.declareProtected(ModifyPortalContent, 'orderObjects')
    def orderObjects(self, key, reverse=None):
        """Order sub-objects by key and direction."""
        ids = [id for id, obj in sort(self.objectItems(),
                                      ((key, 'cmp', 'asc'),))]
        if reverse:
            ids.reverse()
        return self.moveObjectsByDelta(ids, -len(self._objects))

    # Here the implementation of IOrderedContainer ends

    def manage_renameObject(self, id, new_id, REQUEST=None):
        """Rename a particular sub-object."""
        objidx = self.getObjectPosition(id)
        method = OrderedContainer.inheritedAttribute('manage_renameObject')
        result = method(self, id, new_id, REQUEST)
        self.moveObject(new_id, objidx)
        putils = getToolByName(self, 'plone_utils')
        putils.reindexOnReorder(self)
        return result

InitializeClass(OrderedContainer)

class BasePloneFolder(CMFCatalogAware, PortalFolderBase, DefaultDublinCoreImpl):
    """Implements basic Plone folder functionality except ordering support.
    """

    security = ClassSecurityInfo()

    implements(IWriteLock)

    manage_options = Folder.manage_options + \
                     CMFCatalogAware.manage_options

    # Fix permissions set by CopySupport.py
    __ac_permissions__ = (
        ('Modify portal content',
         ('manage_cutObjects', 'manage_pasteObjects',
          'manage_renameForm', 'manage_renameObject',
          'manage_renameObjects',)),
        )

    security.declareProtected(Permissions.copy_or_move, 'manage_copyObjects')

    def __init__(self, id, title=''):
        DefaultDublinCoreImpl.__init__(self)
        self.id = id
        self.title = title

    def __call__(self):
        """Invokes the default view."""
        ti = self.getTypeInfo()
        method_id = ti and ti.queryMethodId('(Default)', context=self)
        if method_id:
            method = getattr(self, method_id)
            # XXX view is not defined!
            if getattr(aq_base(view), 'isDocTemp', 0):
                return method(self, self.REQUEST, self.REQUEST['RESPONSE'])
            else:
                return method()
        else:
            raise NotFound( 'Cannot find default view for "%s"' %
                            '/'.join( self.getPhysicalPath() ) )

    security.declareProtected(Permissions.view, 'view')
    view = __call__

    def index_html(self):
        """Acquire if not present."""
        request = getattr(self, 'REQUEST', None)
        if request and request.has_key('REQUEST_METHOD'):
            if request.maybe_webdav_client:
                method = request['REQUEST_METHOD']
                if method in ('PUT',):
                    # Very likely a WebDAV client trying to create something
                    return ReplaceableWrapper(NullResource(self, 'index_html'))
                elif method in ('GET', 'HEAD', 'POST'):
                    # Do nothing, let it go and acquire.
                    pass
                else:
                    raise AttributeError, 'index_html'
        # Acquire from parent
        _target = aq_parent(aq_inner(self)).aq_acquire('index_html')
        return ReplaceableWrapper(aq_base(_target).__of__(self))

    index_html = ComputedAttribute(index_html, 1)

    security.declareProtected(AddPortalFolders, 'manage_addPloneFolder')
    def manage_addPloneFolder(self, id, title='', REQUEST=None):
        """Adds a new PloneFolder."""
        ob = PloneFolder(id, title)
        self._setObject(id, ob)
        if REQUEST is not None:
            # TODO HARDCODED FIXME!
            return self.folder_contents(self, REQUEST)

    manage_addFolder = manage_addPloneFolder
    manage_renameObject = PortalFolderBase.manage_renameObject

    security.declareProtected(Permissions.delete_objects, 'manage_delObjects')
    def manage_delObjects(self, ids=[], REQUEST=None):
        """We need to enforce security."""
        mt = getToolByName(self, 'portal_membership')
        if type(ids) is StringType:
            ids = [ids]
        for id in ids:
            item = self._getOb(id)
            if not mt.checkPermission(Permissions.delete_objects, item):
                raise Unauthorized, (
                    "Do not have permissions to remove this object")
        return PortalFolderBase.manage_delObjects(self, ids, REQUEST=REQUEST)

    def __browser_default__(self, request):
        """Set default so we can return whatever we want instead
        of index_html."""
        return getToolByName(self, 'plone_utils').browserDefault(self)

    security.declarePublic('contentValues')
    def contentValues(self, filter=None, sort_on=None, reverse=0):
        """Able to sort on field."""
        values = PortalFolderBase.contentValues(self, filter=filter)
        if sort_on is not None:
            values.sort(lambda x, y,
                        sort_on=sort_on: safe_cmp(getattr(x,sort_on),
                                                  getattr(y,sort_on)))
        if reverse:
            values.reverse()

        return values

    security.declareProtected(ListFolderContents, 'listFolderContents')
    def listFolderContents(self, contentFilter=None,
                           suppressHiddenFiles=0):
        """Optionally you can suppress "hidden" files, or files that
        begin with .
        """
        contents = PortalFolderBase.listFolderContents(self,
                                                  contentFilter=contentFilter)
        if suppressHiddenFiles:
            contents = [obj for obj in contents if obj.getId()[:1]!='.']
        return contents

    security.declareProtected(AccessContentsInformation,
                              'folderlistingFolderContents')
    def folderlistingFolderContents(self, contentFilter=None,
                                    suppressHiddenFiles=0):
        """Calls listFolderContents in protected only by ACI so that
        folder_listing can work without the List folder contents permission,
        as in CMFDefault.
        """
        return self.listFolderContents(contentFilter, suppressHiddenFiles)

    # Override CMFCore's invokeFactory to return the id returned by the
    # factory in case the factory modifies the id
    security.declareProtected(AddPortalContent, 'invokeFactory')
    def invokeFactory(self, type_name, id, RESPONSE=None, *args, **kw):
        """Invokes the portal_types tool."""
        pt = getToolByName(self, 'portal_types')
        myType = pt.getTypeInfo(self)
        if myType is not None:
            if not myType.allowType(type_name):
                raise ValueError, 'Disallowed subobject type: %s' % type_name
        args = (type_name, self, id, RESPONSE) + args
        new_id = pt.constructContent(*args, **kw)
        if new_id is None or new_id == '':
            new_id = id
        return new_id

InitializeClass(BasePloneFolder)

class PloneFolder(BasePloneFolder, OrderedContainer):
    """A Plone Folder."""
    meta_type = 'Plone Folder'
    security=ClassSecurityInfo()

    manage_renameObject = OrderedContainer.manage_renameObject
    security.declareProtected(Permissions.copy_or_move, 'manage_copyObjects')

InitializeClass(PloneFolder)

def safe_cmp(x, y):
    if callable(x): x=x()
    if callable(y): y=y()
    return cmp(x,y)

def addPloneFolder(self, id, title='', description='', REQUEST=None):
    """Adds a Plone Folder."""
    sf = PloneFolder(id, title=title)
    sf.description=description
    self._setObject(id, sf)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(sf.absolute_url() + '/manage_main')
