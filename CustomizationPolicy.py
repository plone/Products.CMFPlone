#These CustomizationPolicies *are not* persisted!!
from OFS.PropertyManager import PropertyManager
from Products.CMFPlone.Portal import addPolicy
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions
from interfaces.CustomizationPolicy import ICustomizationPolicy

ExtInstalled=0

def register(context, app_state):
    addPolicy('Default Plone', DefaultCustomizationPolicy())

class DefaultCustomizationPolicy:
    """ Customizes various actions on CMF tools """
    __implements__ = ICustomizationPolicy

    def addSiteProperties(self, portal):
        """ adds site_properties in portal_properties """
        id='site_properties'
        title='Site wide properties'
        p=PropertyManager('id')
        if id not in portal.portal_properties.objectIds():
            portal.portal_properties.addPropertySheet(id, title, p)

        p=getattr(portal.portal_properties, id)

        #Now we add the lagniappe
        if not hasattr(p,'allowAnonymousViewAbout'): p._setProperty('allowAnonymousViewAbout', 1, 'boolean')
        if not hasattr(p,'localTimeFormat'): p._setProperty('localTimeFormat', '%Y-%m-%d', 'string')
        if not hasattr(p,'localLongTimeFormat'): p._setProperty('localLongTimeFormat', '%Y-%m-%d %I:%M %p', 'string')
        if not hasattr(p,'default_language'): p._setProperty('default_language', 'en', 'string')
        if not hasattr(p,'default_charset'): p._setProperty('default_charset', 'utf-8', 'string')
        if not hasattr(p,'use_folder_tabs'): p._setProperty('use_folder_tabs',('Folder',), 'lines')
        if not hasattr(p,'use_folder_contents'): p._setProperty('use_folder_contents',('Folder',), 'lines')
        if not hasattr(p,'ext_editor'): p._setProperty('ext_editor', ExtInstalled, 'boolean')
        if not hasattr(p, 'available_editors'):
            p._setProperty('available_editors', ('None', ), 'lines')
        if not hasattr(p, 'allowRolesToAddKeywords'): p._setProperty('allowRolesToAddKeywords', ['Manager', 'Reviewer'], 'lines')

    def setupDefaultSlots(self, portal):
        """ sets up the slots on objectmanagers """
        #add the slots to the portal folder
        left_slots=( 'here/navigation_tree_slot/macros/navigationBox'
                   , 'here/login_slot/macros/loginBox'
                   , 'here/about_slot/macros/aboutBox'
                   , 'here/related_slot/macros/relatedBox' )
        right_slots=( 'here/workflow_review_slot/macros/review_box'
                    , 'here/calendar_slot/macros/calendarBox' )
        portal._setProperty('left_slots', left_slots, 'lines')
        portal._setProperty('right_slots', right_slots, 'lines')
        portal.Members._setProperty('right_slots', (), 'lines')

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

    def assignTitles(self, portal):
        titles={'portal_actions':'Contains custom tabs and buttons',
         'portal_membership':'Handles membership policies',
         'portal_memberdata':'Handles the available properties on Members',
         'portal_undo':'Defines actions and functionality related to undo',
         'portal_types':'Controls the available Content Types in your portal',
         'plone_utils':'Various Plone Utility methods',
         'portal_navigation':'Responsible for redirecting to the right page in forms',
         'portal_metadata':'Controls metadata - like keywords, copyrights etc',
         'portal_migration':'Handles migrations to newer Plone versions',
         'portal_registration':'Handles registration of new users',
         'portal_skins':'Controls skin behaviour (search order etc)',
         'portal_syndication':'Generates RSS for folders',
         'portal_workflow':'Contains workflow definitions for your portal',
         'portal_url':'Methods to anchor you to the root of your Plone site',
         'portal_form':'Used together with templates to do validation and navigation',
         'portal_discussion':'Controls how discussions are stored by default on content',
         'portal_catalog':'Indexes all content in the site',
         'portal_form_validation':'Deprecated, not in use',
         'portal_factory':'Responsible for the creation of content objects',
         'portal_calendar':'Controls how Events are shown'
         }

        for o in portal.objectValues():
            title=titles.get(o.getId(), None)
            if title:
                o.title=title

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

        actions_tool=getToolByName(portal, 'portal_registration')
        actions=actions_tool._cloneActions()
        for action in actions:
                if action.id=='join':
                    action.action=Expression('string:${portal_url}/portal_form/join_form')
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
        #get rid of the download tab on File, the view has a download button
        file_actions=tt['File']._cloneActions()
        tt['File']._actions=[action for action in file_actions if action['id']!='download']

        #change all Metadata labels to Properties for usability
        for t in tt.objectValues():
            _actions=t._cloneActions()
            for a in _actions:
                if a.get('id','')=='metadata':
                    a['name']='Properties'
            t._actions=_actions
        #add custom Plone actions
        at=getToolByName(portal, 'portal_actions')
        at_actions=at._cloneActions()
        for a in at_actions:
            if a.id=='folderContents' and a.category=='object':
                a.visible=0
            if a.id=='folderContents' and a.category=='folder':
                a.title='Folder Contents'
        at._actions=at_actions

        at.addAction('index_html','Welcome','portal_url','', 'View', 'portal_tabs')
        at.addAction('Members','Members','string:$portal_url/Members','','View','portal_tabs')
        at.addAction('news','News','string:$portal_url/news','','View', 'portal_tabs')
        at.addAction('search_form','Search','string:$portal_url/search_form','','View','portal_tabs')

        at.addAction( 'content_status_history'
                    , 'State'
                    , 'string:${object_url}/content_status_history'
                    , 'python:object and portal.portal_workflow.getTransitionsFor(object, object.getParentNode())'
                    , 'View'
                    , 'object_tabs' )
        at.addAction( 'change_ownership', 'Ownership', 'string:${object_url}/ownership_form', '', CMFCorePermissions.ManagePortal, 'object_tabs', 0)

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

        #customize memberdata tool
        md=getToolByName(portal, 'portal_memberdata')
        if not hasattr(md,'formtooltips'):
            md._setProperty('formtooltips', '1', 'boolean')
        if not hasattr(md,'visible_ids'):
            md._setProperty('visible_ids', '1', 'boolean')
        if not hasattr(md,'wysiwyg_editor'):
            md._setProperty('wysiwyg_editor', '', 'string')
        if not hasattr(md,'listed'):
            md._setProperty('listed', '1', 'boolean')
        else:
            md._setPropValue('listed','1')
        if not hasattr(md, 'fullname'):
            md._setProperty('fullname', '', 'string')

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
            if a.id=='login':
                a.title='Log in'
            if a.id=='logout':
                a.title='Log out'
            if a.id=='preferences':
                a.title='My Preferences'
                a.action=Expression('string:${portal_url}/portal_form/personalize_form')
                new_actions.insert(0, a)
            if getattr(a,'id','') in ('addFavorite', 'favorites'):
                a.visible=0
                new_actions.insert(1,a)
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
        if hasattr(portal, 'portal_registration'):
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

        #add quick-undo to portal_undo
        ut=getToolByName(portal, 'portal_undo')
        ut.addAction( 'undo'
                    , 'Quick Undo'
                    , 'string:${object_url}/quick_undo'
                    , 'member'
                    , CMFCorePermissions.UndoChanges
                    , 'user'
                    , visible=0)

        #the new plone actions are prefix with 'portal_form/'  this
        #ensures a special proxy object shadows content objects and
        #they can participate in validation/navigation
        self.plonify_typeActions(portal)

        #remove non Plone skins from skins tool
        #since we implemented the portal_form proxy these skins will no longer work
        st=getToolByName(portal, 'portal_skins')
        skins_map=st._getSelections()
        if skins_map.has_key('No CSS'):
            del skins_map['No CSS']
        if skins_map.has_key('Nouvelle'):
            del skins_map['Nouvelle']
        if skins_map.has_key('Basic'):
            del skins_map['Basic']
        st.selections=skins_map

        #set up cookie crumbler
        cookie_authentication = getToolByName(portal, 'cookie_authentication')
        cookie_authentication._updateProperty('auto_login_page', 'require_login')


        self.setupDefaultSlots(portal)
        self.addSiteProperties(portal)
        self.assignTitles(portal)
