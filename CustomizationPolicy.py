#These CustomizationPolicies *are not* persisted!!

from Products.CMFPlone.Portal import addPolicy
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions
from interfaces.CustomizationPolicy import ICustomizationPolicy

def register(context, app_state):
    addPolicy('Default Plone', DefaultCustomizationPolicy())
    
class DefaultCustomizationPolicy:
    """ Customizes various actions on CMF tools """
    __implements__ = ICustomizationPolicy

    def installExternalEditor(self, portal):
        ''' responsible for doing whats necessary if 
            external editor is found 
        '''
        types_tool=getToolByName(portal, 'portal_types')
        methods=('PUT', 'manage_FTPget') #if a definition has these methods it shoudl work
        exclude=('Topic', 'Event', 'Folder')
        for ctype in types_tool.objectValues():
            if ctype.getId() not in exclude:
                ctype.addAction( 'external_edit'
                               , 'External Edit'
                               , 'external_edit'
                               , CMFCorePermissions.ModifyPortalContent
                               , 'object'
                               , 0 )
            
        
    def customize(self, portal):
        #make 'reply' tab unvisible
        dt=getToolByName(portal, 'portal_discussion') 
        dt_actions=dt._cloneActions()        
        for a in dt_actions: 
            if a.id=='reply': a.visible=0
        dt._actions=dt_actions

        #make 'syndication' tab unvisible
        st=getToolByName(portal, 'portal_syndication')
        st_actions=st._cloneActions()
        for a in st_actions:
            if a.id=='syndication': a.visible=0
        st._actions=st_actions

        #now lets get rid of folder_listing/folder_contents tabs for folder objects
        tt=getToolByName(portal, 'portal_types')
        folder_actions=tt['Folder']._cloneActions()
        for a in folder_actions:
            if a.get('id','') in ('folderlisting', ): a['visible']=0
        tt['Folder']._actions=folder_actions

        tt['Event'].addAction( 'metadata'
                             , 'Metadata'
                             , 'metadata_edit_form'
                             , CMFCorePermissions.ModifyPortalContent
                             , 'object' )

        #change all Metadata labels to Properties for usability
        for t in tt.objectValues():
            _actions=t._cloneActions()
            for a in _actions:
                if a.get('id','')=='metadata':
                    a['name']='Properties'
            t._actions=_actions
        
        #add custom Plone actions
        at=getToolByName(portal, 'portal_actions')
        at.addAction('index_html','Welcome','portal_url','', 'View', 'portal_tabs')
        at.addAction('Members','Members','string: $portal_url/Members/roster','','List portal members','portal_tabs')
        at.addAction('news','News','string: $portal_url/news','','View', 'portal_tabs')	
        at.addAction('search_form','Search','string: $portal_url/search_form','','View','portal_tabs')

        at.addAction( 'content_status_history'
                    , 'Publishing'
                    , 'string:${object_url}/content_status_history'
                    , 'python:test(member and portal.plone_utils.getWorkflowChainFor(object), 1, 0)'
                    , 'View'
                    , 'object_tabs' )

        at.addAction('rename','Rename','string:folder_rename_form:method','', CMFCorePermissions.ModifyPortalContent, 'folder_buttons')
        at.addAction('cut', 'Cut', 'string:folder_cut:method', '', CMFCorePermissions.ModifyPortalContent, 'folder_buttons')
        at.addAction('copy', 'Copy', 'string:folder_copy:method', '', CMFCorePermissions.ModifyPortalContent, 'folder_buttons')
        at.addAction('paste', 'Paste', 'string:folder_paste:method', 'folder/cb_dataValid', CMFCorePermissions.ModifyPortalContent, 'folder_buttons')
        at.addAction('delete', 'Delete', 'string:folder_delete:method', '', CMFCorePermissions.ModifyPortalContent, 'folder_buttons')
        at.addAction('change_status', 'Change Status', 'string:content_status_history:method', '', CMFCorePermissions.ModifyPortalContent, 'folder_buttons')

        #add properties on portal object
        
        ExtInstalled=0
        ExtEditProd=getattr(portal.Control_Panel.Products, 'ExternalEditor', None)
        if ExtEditProd is not None and ExtEditProd.import_error_ is None:
            ExtInstalled=1
            self.installExternalEditor(portal)

        portal._setProperty('ext_editor', ExtInstalled, 'boolean')
        portal._setProperty('available_editors', ('None', 'XSDHTMLEditor'), 'lines')

        #customize memberdata tool
        md=getToolByName(portal, 'portal_memberdata')
        md._setProperty('formtooltips', '1', 'boolean')
        md._setProperty('visible_ids', '', 'boolean')
        md._setProperty('wysiwyg_editor', 'available_editors', 'selection')

        #customize membership tool
        mt=getToolByName(portal, 'portal_membership')
        mt.addAction('myworkspace'
                    ,'My Workspace'
                    ,'python: portal.portal_membership.getHomeUrl()+"/workspace"'
                    ,'python: member and portal.portal_membership.getHomeFolder()'
                    ,'View'
                    ,'user'
                    , visible=0)		    
        new_actions=[]
        for a in mt._cloneActions():
            if getattr(a,'id','') in ('addFavorite', 'favorites'): 
                a.visible=0
            if a.id=='mystuff': 
                new_actions.insert(0, a)
            elif a.id=='myworkspace':
                new_actions.insert(1, a)
            elif a.id=='logout':
                new_actions.append(a)
            else:
                new_actions.insert(len(new_actions)-1,a)
        mt._actions=new_actions
        
        #customized the registration tool
        rt=getToolByName(portal, 'portal_registration')
        rt_actions=rt._cloneActions()
        for a in rt_actions:
            if a.id=='join':
                a.condition=Expression('python: test(not member and portal.portal_membership.checkPermission("Add portal member", portal), 1, 0)')
        rt._actions=rt_actions
	
        pp=getToolByName(portal, 'portal_properties')
        pp_actions=pp._cloneActions()
        for a in pp_actions:
            if a.id=='configPortal':
                a.title='Plone Setup'
        pp._actions=pp_actions

