#These CustomizationPolicies *are not* persisted!!

from Products.CMFPlone.Portal import addPolicy
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from interfaces.CustomizationPolicy import ICustomizationPolicy

def register(context, app_state):
    addPolicy('Default Plone', DefaultCustomizationPolicy())
    
class DefaultCustomizationPolicy:
    """ Customizes various actions on CMF tools """
    __implements__ = ICustomizationPolicy

    def customize(self, portal):
	#make 'reply' tab unvisible
        dt=getToolByName(portal, 'portal_discussion') 
	dt_actions=dt.listActions()        
        for a in dt_actions: 
            if a.id=='reply': a.visible=0
        dt._actions=dt_actions

        #make 'syndication' tab unvisible
        st=getToolByName(portal, 'portal_syndication')
        st_actions=st.listActions()
        for a in st_actions:
            if a.id=='syndication': a.visible=0
        st._actions=st_actions

        #now lets get rid of folder_listing/folder_contents tabs for folder objects
        tt=getToolByName(portal, 'portal_types')
	folder_actions=tt['Folder']._actions[:]
        for a in folder_actions:
            if a.get('id','') in ('folderlisting', ): a['visible']=0
        tt['Folder']._actions=folder_actions

	#add custom Plone actions
        at=getToolByName(portal, 'portal_actions')
        at.addAction('index_html','Welcome','portal_url','', 'View', 'global_tabs')
        at.addAction('Members','Members','string: $portal_url/Members/roster','','List portal members','global_tabs')
        at.addAction('news','News','string: $portal_url/news','','View', 'global_tabs')	
        at.addAction('search_form','Search','string: $portal_url/search_form','','View','global_tabs')
        at.addAction('content_status_history','Publishing','string:${object_url}/content_status_history','','View','local_tabs')
        at.addAction('rename','Rename','string:folder_rename_form:method','','List folder contents', 'local_buttons')
        at.addAction('cut', 'Cut', 'string:folder_cut:method', '', 'List folder contents', 'local_buttons')
        at.addAction('copy', 'Copy', 'string:folder_copy:method', '', 'List folder contents', 'local_buttons')
        at.addAction('paste', 'Paste', 'string:folder_paste:method', 'folder/cb_dataValid', 'List folder contents', 'local_buttons')
        at.addAction('delete', 'Delete', 'string:folder_delete:method', '', 'List folder contents', 'local_buttons')
        at.addAction('change_status', 'Change Status', 'string:content_status_history:method', '', 'List folder contents', 'local_buttons')

	#customize membership tool
        mt=getToolByName(portal, 'portal_membership')
        m_actions=mt.listActions()
        for a in m_actions:
            if getattr(a,'id','') in ('addFavorite', 'favorites'): a.visible=0
        mt._actions=m_actions        
        mt.addAction('myworkspace'
                    ,'My Workspace'
                    ,'python: portal.portal_membership.getHomeUrl()+"/workspace"'
                    ,'python: member and portal.portal_membership.getHomeFolder()'
                    ,'View'
                    ,'user')
        
	#customized the registration tool
        rt=getToolByName(portal, 'portal_registration')
        rt_actions=rt.listActions()
        for a in rt_actions:
            if a.id=='join':
                a.condition=Expression('python: test(not member and portal.portal_membership.checkPermission("Add portal member", portal), 1, 0)')
        rt._actions=rt_actions
	
