from Products.CMFCore.utils import _verifyActionPermissions
from Products.CMFCore.Skinnable import SkinnableObjectManager
from Products.CMFCore.CMFCorePermissions import View, ManageProperties, ListFolderContents
from Products.CMFCore.CMFCorePermissions import AddPortalFolders, AddPortalContent
from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from AccessControl import Permissions, getSecurityManager, ClassSecurityInfo, Unauthorized
from Products.CMFCore import CMFCorePermissions
from Acquisition import aq_base
from Globals import InitializeClass

factory_type_information = ( { 'id'             : 'Folder'
                             , 'meta_type'      : 'Plone Folder'
                             , 'description'    : """\
Plone folders can define custom 'view' actions, or will behave like directory listings without one defined.."""
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

class PloneFolder ( SkinnedFolder ):
    meta_type = 'Plone Folder' 
    security=ClassSecurityInfo()

    def __call__(self):
        '''
        Invokes the default view.
        '''
        view = _getViewFor(self, 'view', 'folderlisting')
        if getattr(aq_base(view), 'isDocTemp', 0):
            return apply(view, (self, self.REQUEST))
        else:
             return view()

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
       
    security.declareProtected( ListFolderContents, 'listFolderContents')
    def listFolderContents( self, spec=None, contentFilter=None, suppressHiddenFiles=0 ): # XXX
        """
        Hook around 'contentValues' to let 'folder_contents'
        be protected.  Duplicating skip_unauthorized behavior of dtml-in.

	we also do not wanat to show objects that begin with a .
        """
        items = self.contentValues(spec=spec, filter=contentFilter)
        l = []
        for obj in items:
            id = obj.getId()
            v = obj
            try:
                if id[0]=='.' and suppressHiddenFiles:
                    raise Unauthorized(id, v)
                if getSecurityManager().validate(self, self, id, v):
                    l.append(obj)
            except Unauthorized:
                pass
        return l

def _getViewFor(obj, view='view', default=None):
    ti = obj.getTypeInfo()
    #import pdb; pdb.set_trace()
    if ti is not None:
        actions = ti.getActions()
        for action in actions:
            if action.get('id', None) == default:
                default=action
            if action.get('id', None) == view:
                if _verifyActionPermissions(obj, action) and action['action']!='':
                    return obj.restrictedTraverse(action['action'])

        # not Best Effort(tm) just yet
        if default is not None:    
            if _verifyActionPermissions(obj, default):
                return obj.restrictedTraverse(default['action'])

        # "view" action is not present or not allowed.
        # Find something that's allowed.
        #for action in actions:
        #    if _verifyActionPermissions(obj, action)  and action.get('action','')!='':
        #        return obj.restrictedTraverse(action['action'])
        raise 'Unauthorized', ('No accessible views available for %s' %
                               string.join(obj.getPhysicalPath(), '/'))
    else:
        raise 'Not Found', ('Cannot find default view for "%s"' %
                            string.join(obj.getPhysicalPath(), '/'))

manage_addPloneFolder=PloneFolder.manage_addPloneFolder

def addPloneFolder( self, id, title='', description='', REQUEST=None ):
    """ adds a Plone Folder """
    sf = PloneFolder( id, title=title)
    sf.description=description
    self._setObject( id, sf )
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

InitializeClass(PloneFolder)
