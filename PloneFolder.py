from __future__ import nested_scopes

from Products.CMFCore.utils import _verifyActionPermissions, getToolByName
from Products.CMFCore.Skinnable import SkinnableObjectManager
from OFS.Folder import Folder
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.CMFCorePermissions import View, ManageProperties, ListFolderContents
from Products.CMFCore.CMFCorePermissions import AddPortalFolders, AddPortalContent
from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.interfaces.DublinCore import DublinCore as IDublinCore
from AccessControl import Permissions, getSecurityManager, ClassSecurityInfo, Unauthorized
from Products.CMFCore import CMFCorePermissions
from Acquisition import aq_base
from Globals import InitializeClass
from webdav.WriteLockInterface import WriteLockInterface

from PloneUtilities import log

factory_type_information = ( { 'id'             : 'Folder'
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
                                  , 'action'        : ''
                                  , 'permissions'   :
                                     (CMFCorePermissions.View,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'folderlisting'
                                  , 'name'          : 'Folder Listing'
                                  , 'action'        : 'folder_listing'
                                  , 'permissions'   :
                                     (Permissions.access_contents_information,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'local_roles'
                                  , 'name'          : 'Local Roles'
                                  , 'action'        : 'folder_localrole_form'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'folder_edit_form'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                )
                             }
                           ,
                           )

class PloneFolder ( SkinnedFolder, DefaultDublinCoreImpl ):
    meta_type = 'Plone Folder' 
    security=ClassSecurityInfo()
    
    __implements__ = (DefaultDublinCoreImpl.__implements__ ,
                      WriteLockInterface)

    manage_options = Folder.manage_options + \
                     CMFCatalogAware.manage_options

    # fix permissions set by CopySupport.py
    __ac_permissions__=(
        ('Modify portal content',
         ('manage_cutObjects', 'manage_copyObjects', 'manage_pasteObjects',
          'manage_renameForm', 'manage_renameObject', 'manage_renameObjects',)),
        )
    
    def __init__(self, id, title=''):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.title=title

    def __call__(self):
        '''
        Invokes the default view.
        '''
        view = _getViewFor(self, 'view', 'folderlisting')
        if getattr(aq_base(view), 'isDocTemp', 0):
            return apply(view, (self, self.REQUEST))
        else:
             return view()

    ### DefaultDublinCoreImpl.editMetadata() has a very bad assumption
    ### which it does not declare in its interface which is 
    ### failIflocked
    def failIfLocked(self):
        """ failIfLocked is used for WEBDAV locking """
        plone=getToolByName(self, 'plone_utils')
        #log(self.absolute_url() + " failIfLocked called on Plone Folder" )
        return 0
    
    ### FIXME! SkinnedFolder Creator method doesnt work when creating
    ### objects via Python (eg: on a unittest) apparently because of
    ### a missing context
    Creator = DefaultDublinCoreImpl.Creator
   
    security.declarePublic('contentValues')
    def contentValues(self,
                      spec=None,
                      filter=None,
                      sort_on=None,
                      reverse=0):
        """ Able to sort on field """
        values=SkinnedFolder.contentValues(self, spec=spec, filter=filter)
        if sort_on is not None:
            values.sort(lambda x, y: safe_cmp(getattr(x,sort_on),
                                              getattr(y,sort_on)))
        if reverse:
           values.reverse()

        return values

    security.declareProtected( CMFCorePermissions.View, 'view' )    
    view = __call__
    index_html = None

    security.declareProtected(AddPortalFolders, 'manage_addPloneFolder')
    def manage_addPloneFolder(self, id, title='', REQUEST=None):
        """ adds a new PloneFolder """
        ob=PloneFolder(id, title)
        self._setObject(id, ob)
        if REQUEST is not None:
            return self.folder_contents(self, REQUEST, portal_status_message='Folder added')

    manage_addFolder = manage_addPloneFolder
    manage_addPortalFolder = manage_addPloneFolder

    security.declareProtected( ListFolderContents, 'listFolderContents')
    def listFolderContents( self, spec=None, contentFilter=None, suppressHiddenFiles=0 ): 
        """
        Hook around 'contentValues' to let 'folder_contents'
        be protected.  Duplicating skip_unauthorized behavior of dtml-in.
        
        In the world of Plone we do not want to show objects that begin with a .
        So we have added a simply check.  We probably dont want to raise an
        Exception as much as we want to not show it.
        
        """

        items = self.contentValues(spec=spec, filter=contentFilter)
        l = []
        for obj in items:
            id = obj.getId()
            v = obj
            try:
                if suppressHiddenFiles and id[:1]=='.': 
                    raise Unauthorized(id, v)
                if getSecurityManager().validate(self, self, id, v):
                    l.append(obj)
            except (Unauthorized, 'Unauthorized'):
                pass
        return l

    ### FIXME! SkinnedFolder Creator method doesnt work when creating
    ### objects via Python (eg: on a unittest) apparently because of
    ### a missing context

    Creator = DefaultDublinCoreImpl.Creator

def safe_cmp(x, y):
    if callable(x): x=x()
    if callable(y): y=y()
    return cmp(x,y)

def _getViewFor(obj, view='view', default=None):
    ti = obj.getTypeInfo()
    if ti is not None:
        actions = ti.getActions()
        for action in actions:
            if action.get('id', None) == default:
                default=action
            if action.get('id', None) == view:
                if _verifyActionPermissions(obj, action) and action['action']!='':
                    action = obj.restrictedTraverse(action['action'])
                    if action is not None:
                        return action

        if default is not None:    
            if _verifyActionPermissions(obj, default):
                return obj.restrictedTraverse(default['action'])

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

manage_addPloneFolder=PloneFolder.manage_addPloneFolder

def addPloneFolder( self, id, title='', description='', REQUEST=None ):
    """ adds a Plone Folder """
    sf = PloneFolder( id, title=title)
    sf.description=description
    self._setObject( id, sf )
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

InitializeClass(PloneFolder)

