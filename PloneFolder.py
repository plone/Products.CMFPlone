from Products.CMFCore.utils import _verifyActionPermissions
from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from AccessControl import Permissions
from Products.CMFCore import CMFCorePermissions
from Acquisition import aq_base
from Globals import InitializeClass

factory_type_information = ( { 'id'             : 'Plone Folder'
                             , 'meta_type'      : 'Plone Folder'
                             , 'description'    : """\
Plone folders can define custom 'view' actions, without a view action it will present a directory listing."""
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
                                , { 'id'            : 'foldercontents'
                                  , 'name'          : 'Folder Contents'
                                  , 'action'        : 'folder_contents'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ListFolderContents,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'folder_edit_form'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'syndication'
                                  , 'name'          : 'Syndication'
                                  , 'action'        : 'synPropertiesForm'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                )
                             }
                           ,
                           )


DefaultSkinnedFolder = SkinnedFolder
class PloneFolder ( DefaultSkinnedFolder ):
    meta_type = 'Plone Folder' 

    def __call__(self):
        '''
        Invokes the default view.
        '''
        view = _getViewFor(self, 'index_html', 'folderlisting')
        if getattr(aq_base(view), 'isDocTemp', 0):
            return apply(view, (self, self.REQUEST))
        else:
             return view()

    view = __call__

def _getViewFor(obj, view='view', default=None):
    ti = obj.getTypeInfo()
    if ti is not None:
        actions = ti.getActions()
        for action in actions:
            if action.get('id', None) == default:
                default=action
            if action.get('id', None) == view:
                if _verifyActionPermissions(obj, action):
                    return obj.restrictedTraverse(action['action'])

        # not Best Effort(tm) just yet
        if default is not None:    
            if _verifyActionPermissions(obj, default):
                return obj.restrictedTraverse(default['action'])

        # "view" action is not present or not allowed.
        # Find something that's allowed.
        for action in actions:
            if _verifyActionPermissions(obj, action):
                return obj.restrictedTraverse(action['action'])
        raise 'Unauthorized', ('No accessible views available for %s' %
                               string.join(obj.getPhysicalPath(), '/'))
    else:
        raise 'Not Found', ('Cannot find default view for "%s"' %
                            string.join(obj.getPhysicalPath(), '/'))

def addPloneFolder( self, id, title='', description='', REQUEST=None ):
    """
    """
    sf = PloneFolder( id, title )
    sf.description = description
    self._setObject( id, sf )
    sf = self._getOb( id )
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

InitializeClass(SkinnedFolder)