from Products.CMFCore.utils import getToolByName
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.ExternalMethod import ExternalMethod

def upgrade(self):
    portal = getToolByName(self, 'portal_url').getPortalObject()
    if not portal.hasProperty('allowAnonymousViewAbout'):
        portal._setProperty('allowAnonymousViewAbout', 0, 'boolean')
        #outStream.write( "By default anonymous is not allowed to see the About box \n" )
    if not 'getWorklists' in self.objectIds():
        em = ExternalMethod.ExternalMethod(id='getWorklists',
                                           title='Plone worklists',
                                           module='CMFPlone.PloneWorklists',
                                           function='getWorklists')
        self._setObject('getWorklists', em)

    return 'fin'

def migrate2ColumnLayout(self):
    skin_tool=getToolByName(self, 'portal_skins')

    debug = getattr(self, 'plone_debug')

    skin_map=skin_tool._getSelections()

    map = { 'plone_ui_slots': 'plone_templates/ui_slots'
          , 'plone_mozilla': 'plone_styles/mozilla'
          , 'plone_form_scripts': 'plone_scripts/form_scripts'
          , 'plone_ie55': '' #erase plone_ie55 skin entry
          , 'plone_xp': 'plone_styles/winxp'
          }

    for skin_name, skin_path in skin_tool.getSkinPaths():
        fsdir_views = [map.get(path.strip(), path.strip()) for path in skin_path.split(',')]
        path = [p for p in fsdir_views if p]
        skin_map[skin_name]=','.join(path)

def setupButtonActions(self):
    st=getToolByName(self, 'portal_actions')
    st.addAction('rename','Rename','string:folder_rename_form:method','','List folder contents', 'local_buttons')
    st.addAction('cut', 'Cut', 'string:folder_cut:method', '', 'List folder contents', 'local_buttons')
    st.addAction('copy', 'Copy', 'string:folder_copy:method', '', 'List folder contents', 'local_buttons')
    st.addAction('paste', 'Paste', 'string:folder_paste:method', 'folder/cb_dataValid', 'List folder contents', 'local_buttons')
    st.addAction('delete', 'Delete', 'string:folder_delete:method', '', 'List folder contents', 'local_buttons')
    st.addAction('change_status', 'Change Status', 'string:content_status_history:method', '', 'List folder contents', 'local_buttons')
    return 'button setup complete.'
			    
def normalize_tabs(self):
    """ attempts to remove tabs that dont add to user experience """
    #make 'reply' tab unvisible
    dt=getToolByName(self, 'portal_discussion')
    for a in dt._actions:
        if a.id=='reply':
            a.visible=0
    dt._p_changed=1

    #make 'syndication' tab unvisible
    st=getToolByName(self, 'portal_syndication')
    for a in st._actions:
        if a.id=='syndication':
            a.visible=0
    st._p_changed=1

    #now lets get rid of folder_listing/folder_contents tabs for folder objects
    tt=getToolByName(self, 'portal_types')
    folderType=tt['Folder']
    for a in folderType._actions:
        if a.get('id','') in ('folderlisting', ):
            a['visible']=0
    folderType._p_changed=1
    get_transaction().commit(1)

    #at=getToolByName(self, 'portal_actions')
    #at.addAction('index_html','Welcome','portal_url','', 'View', 'global_tabs')
    #get_transaction().commit(1)
    #at.addAction('Members','Members','string: $portal_url/Members/roster','','List portal members','global_tabs')
    #at.addAction('news','News','string: $portal_url/news','','View', 'global_tabs')
    #at.addAction('search_form','Search','string: $portal_url/search_form','','View','global_tabs')
    #at.addAction('content_status_history','Publishing','string:${object_url}/content_status_history','','View','local_tabs')
    #get_transaction().commit(1)
    #move add to favorites 
    mt=getToolByName(self, 'portal_membership')
    #import pdb; pdb.set_trace()
    #m_actions=mt._actions[:]
    m_actions=mt.listActions()
    for a in m_actions:
        if getattr(a,'id','') in ('addFavorite', 'favorites'):
            a.visible=0
    mt._actions=m_actions
    #mt.addAction('myworkspace'
    #            ,'My Workspace'
    #            ,'python: portal.portal_membership.getHomeUrl()+"/workspace"'
    #            ,'python: member and portal.portal_membership.getHomeFolder()'
    #            ,'View'
    #    	,'user')
    #mt._p_changed=1
    get_transaction().commit(1)
    #make 'join' action disappear if anonymous cant add portal member
    #this is aligned with out the 'sign in' box works in ui_slots
    rt=getToolByName(self, 'portal_registration')
    for a in rt._actions:
        if a.id=='join':
            a.condition=Expression('python: test(not member and portal.portal_membership.checkPermission("Add portal member", portal), 1, 0)')
    rt._p_changed=1
    get_transaction().commit(1)
    import time
    return 'finished tab migration at %s ' % time.strftime('%I:%M %p %m/%d/%Y')

def migrate099to10(self):
    portal=getToolByName(self, 'portal_url').getPortalObject()
    if not hasattr(portal, 'localTimeFormat'):
        portal._setProperty('localTimeFormat', '%Y-%m-%d', 'string')

    if not hasattr(portal, 'localLongTimeFormat'):
        portal._setProperty('localLongTimeFormat', '%Y-%m-%d %I:%M %p', 'string')
        
    normalize_tabs(self)
    wt=getToolByName(self, 'portal_workflow')
    wt.manage_delObjects('default_workflow')

    #customize memberdata tool
    md=getToolByName(self, 'portal_memberdata')
    md._setProperty('formtooltips', '1', 'boolean')
    md._setProperty('visible_ids', '', 'boolean')

    return 'finished migraiton'
