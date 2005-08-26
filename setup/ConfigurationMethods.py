from OFS.PropertyManager import PropertyManager
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression
from Products.CMFPlone.migrations.migration_util import safeEditProperty
from Acquisition import aq_get
from AccessControl import Permissions
from Products.SiteErrorLog.SiteErrorLog import manage_addErrorLog
from DateTime import DateTime

from zLOG import INFO, ERROR
from SetupBase import SetupWidget

def addErrorLog(self, portal):
    if "error_log" not in portal.objectIds():
        manage_addErrorLog(portal)
        portal.error_log.copy_to_zlog = 1

def installPortalTools(self,portal):
    ''' This should be done in Products/CMFPlone/Portal.py in setupTools '''
    pass

def addSiteProperties(self, portal):
    """ adds site_properties in portal_properties """
    id = 'site_properties'
    title = 'Site wide properties'
    year = DateTime().year()
    p=PropertyManager('id')
    if id not in portal.portal_properties.objectIds():
        portal.portal_properties.addPropertySheet(id, title, p)
    p=getattr(portal.portal_properties, id)

    if not hasattr(p,'allowAnonymousViewAbout'):
        safeEditProperty(p, 'allowAnonymousViewAbout', 1, 'boolean')
    if not hasattr(p,'localTimeFormat'):
        safeEditProperty(p, 'localTimeFormat', '%Y-%m-%d', 'string')
    if not hasattr(p,'localLongTimeFormat'):
        safeEditProperty(p, 'localLongTimeFormat', '%Y-%m-%d %H:%M', 'string')
    if not hasattr(p,'default_language'):
        safeEditProperty(p, 'default_language', 'en', 'string')
    if not hasattr(p,'default_charset'):
        safeEditProperty(p, 'default_charset', 'utf-8', 'string')
    if not hasattr(p,'use_folder_tabs'):
        safeEditProperty(p, 'use_folder_tabs',('Folder',), 'lines')
    if not hasattr(p,'use_folder_contents'):
        safeEditProperty(p, 'use_folder_contents',[], 'lines')
    if not hasattr(p,'ext_editor'):
        safeEditProperty(p, 'ext_editor', 0, 'boolean')
    if not hasattr(p, 'available_editors'):
        safeEditProperty(p, 'available_editors', ('None', ), 'lines')
    if not hasattr(p, 'allowRolesToAddKeywords'):
        safeEditProperty(p, 'allowRolesToAddKeywords', ['Manager', 'Reviewer'], 'lines')
    if not hasattr(p, 'auth_cookie_length'):
        safeEditProperty(p, 'auth_cookie_length', 0, 'int')
    if not hasattr(p, 'calendar_starting_year'):
        safeEditProperty(p, 'calendar_starting_year', 1999, 'int')
    if not hasattr(p, 'calendar_future_years_available'):
        safeEditProperty(p, 'calendar_future_years_available', 5, 'int')


def setupDefaultLeftRightSlots(self, portal):
    """ sets up the slots on objectmanagers """
    left_slots=( 'here/portlet_navigation/macros/portlet'
               , 'here/portlet_login/macros/portlet'
               , 'here/portlet_recent/macros/portlet'
               , 'here/portlet_related/macros/portlet' )
    right_slots=( 'here/portlet_review/macros/portlet'
                , 'here/portlet_news/macros/portlet'
                , 'here/portlet_events/macros/portlet'
                , 'here/portlet_calendar/macros/portlet' )
    safeEditProperty(portal, 'left_slots', left_slots, 'lines')
    safeEditProperty(portal, 'right_slots', right_slots, 'lines')
    safeEditProperty(portal.Members, 'right_slots', (), 'lines')

def setupDefaultItemActionSlots(self, portal):
    """ Sets up the default action item slots """
    'These are now document_actions ActionInformation object in portal_actiosn'
    pass

def installExternalEditor(self, portal):
    ''' responsible for doing whats necessary if external editor is found '''
    try:
        from Products.ExternalEditor.ExternalEditor import ExternalEditorPermission
    except ImportError:
        pass
    else:
        types_tool=getToolByName(portal, 'portal_types')
        methods=('PUT', 'manage_FTPget')
        exclude=('Topic', 'Event', 'Folder')
        for ctype in types_tool.objectValues():
            if ctype.getId() not in exclude:
                ctype.addAction( 'external_edit',
                                name='External Edit',
                                action='string:$object_url/external_edit',
                                condition='',
                                permission=CMFCorePermissions.ModifyPortalContent,
                                category='object',
                                visible=0 )
        portal.manage_permission(ExternalEditorPermission,
                                 ('Manager', 'Authenticated'), acquire=0)

def assignTitles(self, portal):
    titles={'portal_actions':'Contains custom tabs and buttons',
     'portal_membership':'Handles membership policies',
     'portal_memberdata':'Handles the available properties on members',
     'portal_undo':'Defines actions and functionality related to undo',
     'portal_types':'Controls the available content types in your portal',
     'plone_utils':'Various utility methods',
     'portal_metadata':'Controls metadata like keywords, copyrights, etc',
     'portal_migration':'Handles migrations to newer Plone versions',
     'portal_registration':'Handles registration of new users',
     'portal_skins':'Controls skin behaviour (search order etc)',
     'portal_syndication':'Generates RSS for folders',
     'portal_workflow':'Contains workflow definitions for your portal',
     'portal_url':'Methods to anchor you to the root of your Plone site',
     'portal_discussion':'Controls how discussions are stored',
     'portal_catalog':'Indexes all content in the site',
     'portal_factory':'Responsible for the creation of content objects',
     'portal_calendar':'Controls how events are shown',
     'portal_quickinstaller':'Allows to install/uninstall products',
     'portal_interface':'Allows to query object interfaces',
     'portal_actionicons':'Associates actions with icons',
     'portal_groupdata':'Handles properties on groups',
     'portal_groups':'Handles group related functionality',
     'translation_service': 'Provides access to the translation machinery',
     'mimetypes_registry': 'MIME types recognized by Plone',
     'portal_transforms': 'Handles data conversion between MIME types',
     }

    for oid in portal.objectIds():
        title=titles.get(oid, None)
        if title:
            setattr(aq_get(portal, oid), 'title', title)

def addMemberdata(self, portal):
    md=getToolByName(portal, 'portal_memberdata')
    if not hasattr(md,'wysiwyg_editor'):
        safeEditProperty(md, 'wysiwyg_editor', '', 'string')

    if not hasattr(md,'ext_editor'):
        safeEditProperty(md, 'ext_editor', 0, 'boolean')
    else:
        safeEditProperty(md, 'ext_editor', 0)
        
    if not hasattr(md,'listed'):
        safeEditProperty(md, 'listed', '1', 'boolean')
    else:
        safeEditProperty(md, 'listed','1')
        
    if not hasattr(md, 'fullname'):
        safeEditProperty(md, 'fullname', '', 'string')
    if not hasattr(md, 'error_log_update'):
        safeEditProperty(md, 'error_log_update', 0.0, 'float')

def modifyActionProviders(self, portal):
    mt=getToolByName(portal, 'portal_properties')
    _actions=mt._cloneActions()
    for action in _actions:
        if action.id=='configPortal':
            action.visible=0
    mt._actions=_actions

    ut=getToolByName(portal, 'portal_undo')
    _actions=ut._cloneActions()
    for action in _actions:
        if action.id=='undo':
            action.category='user'
    ut._actions=_actions

    at=getToolByName(portal, 'portal_actions')
    correctFolderContentsAction(at)

    dt=getToolByName(portal, 'portal_discussion')
    _actions=dt._cloneActions()
    for action in _actions:
        if action.id=='reply':
            action.visible=0
    dt._actions=_actions

def correctFolderContentsAction(actionTool):
    _actions=actionTool._cloneActions()
    for action in _actions:
        if action.id=='folderContents':
            action.name=action.title='Contents'
            action.condition=Expression('object/displayContentsTab')
            action.permissions=(CMFCorePermissions.ListFolderContents,)
    actionTool._actions=_actions


def modifyMembershipTool(self, portal):
    mt=getToolByName(portal, 'portal_membership')
    mt.addAction('myworkspace'
                ,'Workspace'
                ,'python: portal.portal_membership.getHomeUrl()+"/workspace"'
                ,'python: member and portal.portal_membership.getHomeFolder() is not None'
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
            a.title='Preferences'
            a.action=Expression('string:${portal_url}/plone_memberprefs_panel')
            new_actions.insert(0, a)
        elif a.id in ('addFavorite', 'favorites'):
            a.visible=0
            new_actions.insert(1,a)
        elif a.id=='mystuff':
            a.title='My Folder'
            new_actions.insert(0, a)
        elif a.id=='myworkspace':
            new_actions.insert(1, a)
        elif a.id=='logout':
            new_actions.append(a)
        else:
            new_actions.insert(len(new_actions)-1,a)
    mt._actions=new_actions

def modifySkins(self, portal):
    #remove non Plone skins from skins tool
    #since we implemented the portal_form proxy these skins will no longer work

    # this should be run through the skins setup widget :)
    st=getToolByName(portal, 'portal_skins')
    skins_map=st._getSelections()

    if skins_map.has_key('No CSS'):
        del skins_map['No CSS']
    if skins_map.has_key('Nouvelle'):
        del skins_map['Nouvelle']
    if skins_map.has_key('Basic'):
        del skins_map['Basic']
    st.selections=skins_map

    types=getToolByName(portal, 'portal_types')
    for t in types.objectValues():
        _actions=t._cloneActions()
        for a in _actions:
            if a.id == 'metadata':
                a.name = 'Properties'   #1.3
                a.title = 'Properties'  #1.4
            if a.id == 'local_roles':
                a.name = 'Sharing'
                a.title = 'Sharing'
            if a.id == 'content_status_history':
                a.visible = 0
        #in 2.0 the Sharing tab is on portal_actions ActionProvider
        #this was reverted - yay!
        #t._actions=[a for a in _actions if a.id!='local_roles']

def addNewActions(self, portal):
    at=getToolByName(portal, 'portal_actions')

    at.addAction('index_html',
                 name='Home',
                 action='string:$portal_url',
                 condition='',
                 permission='View',
                 category='portal_tabs')
    at.addAction('change_ownership',
                 name='Ownership',
                 action='string:${object_url}/ownership_form',
                 condition='',
                 permission=CMFCorePermissions.ManagePortal,
                 category='object_tabs',
                 visible=0)
    at.addAction('rename',
                 name='Rename',
                 action='string:folder_rename_form:method',
                 condition='',
                 permission=CMFCorePermissions.AddPortalContent,
                 category='folder_buttons')
    at.addAction('paste',
                 name='Paste',
                 action='string:folder_paste:method',
                 condition='folder/cb_dataValid',
                 permission=CMFCorePermissions.AddPortalContent,
                 category='folder_buttons')
    at.addAction('delete',
                 name='Delete',
                 action='string:folder_delete:method',
                 condition='',
                 permission=Permissions.delete_objects,
                 category='folder_buttons')

    # Move change_state to the bottom
    cloned_actions = at._cloneActions()
    num_actions = len(cloned_actions)
    state_index = 0
    for action in cloned_actions:
        if action.id == 'change_state' and action.category == 'folder_buttons':
            break
        state_index = state_index + 1
    state_action = cloned_actions.pop(state_index)
    cloned_actions.append(state_action)
    at._actions = cloned_actions

def setPortalDefaultPermissions(self, portal):
    portal.manage_permission(CMFCorePermissions.AccessInactivePortalContent,
                                                ('Owner',), acquire=1)

def enableSiteSyndication(self, portal):
    syn_tool = getToolByName(portal, 'portal_syndication')
    syn_tool.editProperties(isAllowed=True)


functions = {
    'addSiteProperties': addSiteProperties,
    'setupDefaultLeftRightSlots': setupDefaultLeftRightSlots,
    'setupDefaultItemActionSlots': setupDefaultItemActionSlots,
    'installExternalEditor': installExternalEditor,
    'assignTitles': assignTitles,
    'addMemberdata': addMemberdata,
    'modifyMembershipTool': modifyMembershipTool,
    'addNewActions': addNewActions,
    'modifySkins': modifySkins,
    'installPortalTools': installPortalTools,
    'modifyActionProviders': modifyActionProviders,
    'addErrorLog':addErrorLog,
    'setPortalDefaultPermissions':setPortalDefaultPermissions,
    'enableSiteSyndication':enableSiteSyndication,
    }

class GeneralSetup(SetupWidget):
    type = 'General Setup'

    description = """This applies a function to the site. These functions are some of the basic
set up features of a site. The chances are you will not want to apply these again. <b>Please note</b>
these functions do not have a uninstall function."""

    functions = functions

    def setup(self):
        pass

    def delItems(self, fns):
        out = []
        out.append(('Currently there is no way to remove a function', INFO))
        return out

    def addItems(self, fns):
        out = []
        for fn in fns:
            self.functions[fn](self, self.portal)
            out.append(('Function %s has been applied' % fn, INFO))
        return out

    def installed(self):
        return []

    def available(self):
        """ Go get the functions """
        return self.functions.keys()
