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
            
    def plonify_typeActions(self, portal):
        #Plone1.0alpha4 we are moving people to use portal_form nav/validation proxy
        types_tool=getToolByName(portal, 'portal_types')
        for ptype in types_tool.objectValues():
            ptype_actions=ptype._cloneActions()            
            for action in ptype_actions:                
                if not action['action'].startswith('portal_form') and \
                    action['id'] in ('edit', 'metadata'): 
                    action['action']='portal_form/'+action['action']
            ptype._actions=tuple(ptype_actions)

        actions_tool=getToolByName(portal, 'portal_actions')
        actions=actions_tool._cloneActions()
        for action in actions:
                if action.id=='content_status_history':
                    action.action=Expression('string:${object_url}/portal_form/content_status_history')
        actions_tool._actions=tuple(actions)

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
            if a.get('id','') in ('folderlisting', ): 
                a['visible'] = 0
            if a.get('id','')=='edit':
                a['name'] = 'Properties'
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
        at.addAction( 'change_ownership', 'Ownership', 'string:${object_url}/ownership_form', '', CMFCorePermissions.ManagePortal, 'object_tabs' )
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
            if a.id=='preferences':
                a.action=Expression('string:${portal_url}/portal_form/personalize_form')
            if getattr(a,'id','') in ('addFavorite', 'favorites'): 
                a.visible=0
            if a.id=='mystuff': 
                a.title='My Folder'
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
                a.action=Expression('string:${portal_url}/portal_form/reconfig_form')
        pp._actions=pp_actions

        #the new plone actions are prefix with 'portal_form/'  this
        #ensures a special proxy object shadows content objects and
        #they can participate in validation/navigation
        self.plonify_typeActions(portal)
        
        #remove non Plone skins from skins tool
        #since we implemented the portal_form proxy these skins will no longer work
        st=getToolByName(portal, 'portal_skins')
        skins_map=st._getSelections()
        del skins_map['No CSS']
        del skins_map['Nouvelle']
        del skins_map['Basic']
        st.selections=skins_map

