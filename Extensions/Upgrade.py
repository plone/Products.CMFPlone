from Products.CMFCore.utils import getToolByName
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

def normalize_tabs(self):
    """ attempts to remove tabs that dont add to user experience """
    #make 'reply' tab unvisible
    dt=getToolByName(self, 'portal_discussion')
    dt_actions=[]
    for a in dt._actions:
        if a.id=='reply':
            a.visible=0
	dt_actions.append(a)    
    dt._actions=dt_actions

    #make 'syndication' tab unvisible
    st=getToolByName(self, 'portal_syndication')
    st_actions=[]
    for a in st._actions:
        if a.id=='syndication':
            a.visible=0
	st_actions.append(a)
    st._actions=st_actions

    #now lets get rid of folder_listing/folder_contents tabs for folder objects
    tt=getToolByName(self, 'portal_types')
    f_actions=tt['Folder']._actions
    actions=[]
    for a in f_actions:
        if a.get('id','') in ('folderlisting', ):
            a['visible']=0
	if a.get('id','') != 'syndication': #syndication tab belongs on syndication tool
            actions.append(a)
    tt['Folder']._actions=actions
 
    get_transaction().commit(1)
    import time
    return 'finished tab migration at %s ' % time.strftime('%I:%M %p %m/%d/%Y')
 
