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
    for button in ( ActionInformation( 'rename'
                                     , title='Rename'
				     , category='local_buttons'
				     , permissions=('List folder contents',)
				     , action=Expression('string:folder_rename_form:method'))
	          , ActionInformation( 'cut'
		                     , title='Cut'
				     , category='local_buttons'
				     , permissions=('List folder contents',)
				     , action=Expression('string:folder_cut:method'))
                  , ActionInformation( 'copy'
		                     , title='Copy'
				     , category='local_buttons'
				     , permissions=('List folder contents',)
				     , action=Expression('string:folder_copy:method'))
	          , ActionInformation( 'paste'
		                     , title='Paste'
				     , category='local_buttons'
				     , permissions=('List folder contents',)
				     , condition=Expression('folder/cb_dataValid')
				     , action=Expression('string:folder_paste:method'))
	          , ActionInformation( 'delete'
		                     , title='Delete'
				     , category='local_buttons'
                                     , permissions=('List folder contents',)
				     , action=Expression('string:folder_delete:method'))
	          , ActionInformation( 'change_status'
		                     , title='Change Status'
				     , category='local_buttons'
				     , permissions=('List folder contents',)
				     , action=Expression('string:content_status_history:method')) ):
        st._actions.append(button)
    st._p_changed=1
    return 'setup complete'
			    
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
    for a in tt['Folder']._actions:
        if a.get('id','') in ('folderlisting', ):
            a['visible']=0
    tt['Folder']._p_changed=1

    def global_tabs():
	welcome=ActionInformation( 'index_html'
	                         , title='Welcome'
				 , category='global_tabs'
				 , permissions=('View',)
				 , action=Expression('portal_url'))
	members=ActionInformation( 'Members'
	                         , title='Members'
				 , category='global_tabs'
				 , permissions=('List portal members',)
				 , action=Expression('string: $portal_url/Members/roster'))
	news=ActionInformation( 'news'
	                      , title='News'
			      , category='global_tabs'
			      , permissions=('View',)
			      , action=Expression('string: $portal_url/news'))
	search=ActionInformation( 'search_form'
	                        , title='Search'
				, category='global_tabs'
				, permissions=('View',)
				, action=Expression('string: $portal_url/search_form'))
	publishing=ActionInformation( 'content_status_history'
                                    , title='Publishing'
                                    , category='local_tabs'
                                    , permissions=('View',)
                                    , condition=Expression("member")
	                           , action=Expression("string: ${object_url}/content_status_history"))
	return (welcome, members, news, search, publishing)
			      
    #make 'syndication' tab unvisible
    st=getToolByName(self, 'portal_actions')
    for globaltab in global_tabs():
        st._actions.append(globaltab)
    st._p_changed=1

    #move add to favorites 
    mt=getToolByName(self, 'portal_membership')
    for x in range(0, len(mt._actions)):
        a=mt._actions[x]
        if a.id=='addFavorite' or \
	   a.id=='favorites':
            a.visible=0
	if a.id=='mystuff':
            mt._actions.insert(0, ActionInformation('mystuff'
	                                          , title='My Stuff'
						  , category=a.category
						  , permissions=a.permissions
						  , condition=Expression(a.condition.text)
						  , action=Expression(a._action.text)))
	    del mt._actions[x+1]
    mt._p_changed=1
    mt._actions.insert(1, ActionInformation( 'myworkspace'
                                          , title='My Workspace'
					  , category='user'
					  , permissions='View'
					  , condition=Expression(
					  'python: member and portal.portal_membership.getHomeFolder()')
					  , action=Expression(
					  'python: portal.portal_membership.getHomeUrl()+"/workspace"')))
    mt._p_changed=1
    #make 'join' action disappear if anonymous cant add portal member
    #this is aligned with out the 'sign in' box works in ui_slots
    rt=getToolByName(self, 'portal_registration')
    for a in rt._actions:
        if a.id=='join':
            a.condition=Expression('python: test(not member and portal.portal_membership.checkPermission("Add portal member", portal), 1, 0)')
    rt._p_changed=1
    
    import time
    return 'finished tab migration at %s ' % time.strftime('%I:%M %p %m/%d/%Y')

def migrate099to10(self):
    portal=getToolByName(self, 'portal_url').getPortalObject()
    if not hasattr(portal, 'localTimeFormat'):
        portal._setProperty('localTimeFormat', '%Y-%m-%d', 'string')
    normalize_tabs(self)
    wt=getToolByName(self, 'portal_workflow')
    wt.manage_delObjects('default_workflow')
    return 'finished migraiton'
