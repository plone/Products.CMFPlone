try: from zExceptions import NotFound
except ImportError: NotFound = 'NotFound' # Zope < 2.7
from Products.CMFCore.utils import _verifyActionPermissions, \
     getToolByName, getActionContext
from OFS.Folder import Folder
from OFS.OrderedFolder import OrderedFolder
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
#from Products.CMFCore.interfaces.DublinCore import DublinCore as IDublinCore
#from Products.CMFCore.interfaces.Contentish import Contentish as IContentish
from AccessControl import Permissions, ClassSecurityInfo, Unauthorized
from Products.CMFCore import CMFCorePermissions
from Acquisition import aq_base, aq_inner, aq_parent
from Globals import InitializeClass
from webdav.WriteLockInterface import WriteLockInterface
from webdav.NullResource import NullResource
from types import StringType
from DocumentTemplate.sequence import sort

from OFS.ObjectManager import REPLACEABLE
from ComputedAttribute import ComputedAttribute

class ReplaceableWrapper:
    """ A wrapper around an object to make it replaceable """
    def __init__(self, ob):
        self.__ob = ob

    def __getattr__(self, name):
        if name == '__replaceable__':
            return REPLACEABLE
        return getattr(self.__ob, name)

factory_type_information = { 'id'             : 'Folder'
                             , 'meta_type'      : 'Plone Folder'
                             , 'description'    : """\
Plone folders can define custom 'view' actions, or will behave like directory listings without one defined."""
                             , 'icon'           : 'folder_icon.gif'
                             , 'product'        : 'CMFPlone'
                             , 'factory'        : 'addPloneFolder'
                             , 'filter_content_types' : 0
                             , 'immediate_view' : 'folder_listing'
                             , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'string:${folder_url}/'
                                  , 'permissions'   :
                                     (CMFCorePermissions.View,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'local_roles'
                                  , 'name'          : 'Local Roles'
                                  , 'action'        : 'string:${folder_url}/folder_localrole_form'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'string:${folder_url}/folder_edit_form'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'folderlisting'
                                  , 'name'          : 'Folder Listing'
                                  , 'action'        : 'string:${folder_url}/folder_listing'
                                  , 'permissions'   :
                                     (CMFCorePermissions.View,)
                                  , 'category'      : 'folder'
                                  , 'visible'       : 0
                                  }
                                )
                             }


class OrderedContainer(OrderedFolder):
    """Folder with subobject ordering support"""
  
    __implements__ = OrderedFolder.__implements__

    security = ClassSecurityInfo()

InitializeClass(OrderedContainer)

class BasePloneFolder( SkinnedFolder, DefaultDublinCoreImpl ):
    """Implements basic Plone folder functionality except ordering support.
    """

    security=ClassSecurityInfo()

    __implements__ =  DefaultDublinCoreImpl.__implements__ + \
                      (SkinnedFolder.__implements__,WriteLockInterface)

    manage_options = Folder.manage_options + \
                     CMFCatalogAware.manage_options
    # fix permissions set by CopySupport.py
    __ac_permissions__=(
        ('Modify portal content',
         ('manage_cutObjects', 'manage_pasteObjects',
          'manage_renameForm', 'manage_renameObject', 'manage_renameObjects',)),
        )

    security.declareProtected(Permissions.copy_or_move, 'manage_copyObjects')

    def __init__(self, id, title=''):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.title=title

    def __call__(self):
        """ Invokes the default view. """
        view = _getViewFor(self, 'view', 'folderlisting')
        if getattr(aq_base(view), 'isDocTemp', 0):
            return view(*(self, self.REQUEST))
        else:
            return view()

    def index_html(self):
        """ Acquire if not present. """
        request = getattr(self, 'REQUEST', None)
        if request and request.has_key('REQUEST_METHOD'):
            if (request.maybe_webdav_client and
                request['REQUEST_METHOD'] in  ['PUT']):
                # Very likely a WebDAV client trying to create something
                return ReplaceableWrapper(NullResource(self, 'index_html'))
        # Acquire from parent
        _target = aq_parent(aq_inner(self)).aq_acquire('index_html')
        return ReplaceableWrapper(aq_base(_target).__of__(self))

    index_html = ComputedAttribute(index_html, 1)

    security.declareProtected(CMFCorePermissions.AddPortalFolders,
                              'manage_addPloneFolder')
    def manage_addPloneFolder(self, id, title='', REQUEST=None):
        """ adds a new PloneFolder """
        ob=PloneFolder(id, title)
        self._setObject(id, ob)
        if REQUEST is not None:
            #XXX HARDCODED FIXME!
            return self.folder_contents(self, REQUEST,
                                        portal_status_message='Folder added')

    manage_addFolder = manage_addPloneFolder
    manage_renameObject = SkinnedFolder.manage_renameObject

    security.declareProtected(Permissions.delete_objects, 'manage_delObjects')
    def manage_delObjects(self, ids=[], REQUEST=None):
        """ We need to enforce security. """
        mt=getToolByName(self, 'portal_membership')
        if type(ids) is StringType:
            ids = [ids]
        for id in ids:
            item = self._getOb(id)
            if not mt.checkPermission(Permissions.delete_objects, item):
                raise Unauthorized, (
                    "Do not have permissions to remove this object")
        SkinnedFolder.manage_delObjects(self, ids, REQUEST=REQUEST)

    def __browser_default__(self, request):
        """ Set default so we can return whatever we want instead
        of index_html """
        return getToolByName(self, 'plone_utils').browserDefault(self)

    security.declarePublic('contentValues')
    def contentValues(self,
                      spec=None,
                      filter=None,
                      sort_on=None,
                      reverse=0):
        """ Able to sort on field """
        values=SkinnedFolder.contentValues(self, spec=spec, filter=filter)
        if sort_on is not None:
            values.sort(lambda x, y, sort_on=sort_on: safe_cmp(getattr(x,sort_on),
                                                               getattr(y,sort_on)))
        if reverse:
            values.reverse()

        return values

    security.declareProtected(CMFCorePermissions.ListFolderContents, 'listFolderContents')
    def listFolderContents( self, spec=None, contentFilter=None, suppressHiddenFiles=0 ):
        """
        Optionally you can suppress "hidden" files, or files that begin with .
        """
        contents=SkinnedFolder.listFolderContents(self,
                                                  spec=spec,
                                                  contentFilter=contentFilter)
        if suppressHiddenFiles:
            contents=[obj for obj in contents if obj.getId()[:1]!='.']

        return contents

    security.declareProtected(CMFCorePermissions.AccessContentsInformation, 'folderlistingFolderContents')
    def folderlistingFolderContents( self, spec=None, contentFilter=None, suppressHiddenFiles=0 ):
        """
        Calls listFolderContents in protected only by ACI so that folder_listing
        can work without the List folder contents permission, as in CMFDefault
        """
        return self.listFolderContents(spec, contentFilter, suppressHiddenFiles)

    # Override CMFCore's invokeFactory to return the id returned by the
    # factory in case the factory modifies the id
    security.declareProtected(CMFCorePermissions.AddPortalContent, 'invokeFactory')
    def invokeFactory( self
                     , type_name
                     , id
                     , RESPONSE=None
                     , *args
                     , **kw
                     ):
        '''Invokes the portal_types tool.'''
        pt = getToolByName( self, 'portal_types' )
        myType = pt.getTypeInfo(self)

        if myType is not None:
            if not myType.allowType( type_name ):
                raise ValueError, 'Disallowed subobject type: %s' % type_name

        args = (type_name, self, id, RESPONSE) + args
        new_id = pt.constructContent(*args, **kw)
        if new_id is None or new_id == '':
            new_id = id
        return new_id

InitializeClass(BasePloneFolder)

class PloneFolder( BasePloneFolder, OrderedContainer ):
    """ A Plone Folder """
    meta_type = 'Plone Folder'
    security=ClassSecurityInfo()
    __implements__ = BasePloneFolder.__implements__ + \
                     OrderedContainer.__implements__

    manage_renameObject = OrderedContainer.manage_renameObject
    security.declareProtected(Permissions.copy_or_move, 'manage_copyObjects')

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'acquireLocalRoles')
    def acquireLocalRoles(self, status = 1):
        """If status is 1, allow acquisition of local roles (regular behaviour).
        If it's 0, prohibit it (it will allow some kind of local role blacklisting).
        GRUF IS REQUIRED FOR THIS TO WORK.
        """
        # Set local role status
        gruf = getToolByName( self, 'portal_url' ).acl_users
        gruf._acquireLocalRoles(self, status)   # We perform our own security check

        # Reindex the whole stuff.
        self.reindexObjectSecurity()

    security.declarePublic("isLocalRoleAcquired")
    def isLocalRoleAcquired(self):
        """GRUF IS REQUIRED FOR THIS TO WORK.
        Return Local Role acquisition blocking status. True if normal, false if blocked.
        """
        gruf = getToolByName( self, 'portal_url' ).acl_users
        return gruf.isLocalRoleAcquired(self, )


InitializeClass(PloneFolder)

def safe_cmp(x, y):
    if callable(x): x=x()
    if callable(y): y=y()
    return cmp(x,y)

def addPloneFolder( self, id, title='', description='', REQUEST=None ):
    """ adds a Plone Folder """
    sf = PloneFolder(id, title=title)
    sf.description=description
    self._setObject(id, sf)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

#--- Helper function that can figure out what 'view' action to return
def _getViewFor(obj, view='view', default=None):

    ti = obj.getTypeInfo()
    context = getActionContext(obj)
    if ti is not None:
        actions = ti.listActions()
        for action in actions:
            _action = action.getAction(context)
            if _action.get('id', None) == default:
                default=action
            if _action.get('id', None) == view:
                target=_action['url']
                if target.startswith('/'):
                    target = target[1:]
                if _verifyActionPermissions(obj, action) and target!='':
                    __traceback_info__ = ( ti.getId(), target )
                    computed_action = obj.restrictedTraverse(target)
                    if computed_action is not None:
                        return computed_action

        if default is not None:
            _action = default.getAction(context)
            if _verifyActionPermissions(obj, default):
                target=_action['url']
                if target.startswith('/'):
                    target = target[1:]
                __traceback_info__ = ( ti.getId(), target )
                return obj.restrictedTraverse(target)

        # "view" action is not present or not allowed.
        # Find something that's allowed.
        #for action in actions:
        #    if _verifyActionPermissions(obj, action)  and action.get('action','')!='':
        #        return obj.restrictedTraverse(action['action'])
        raise 'Unauthorized', ('No accessible views available for %s' %
                               '/'.join(obj.getPhysicalPath()))
    else:
        raise 'Not Found', ('Cannot find default view for "%s"' %
                            '/'.join(obj.getPhysicalPath()))
