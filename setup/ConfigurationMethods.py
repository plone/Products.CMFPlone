from OFS.PropertyManager import PropertyManager
from Products.CMFCore.permissions import ListFolderContents
from Products.CMFCore.Expression import Expression
from Products.CMFPlone.migrations.migration_util import safeEditProperty
from Products.CMFPlone.utils import log_deprecated
from Acquisition import aq_get
from DateTime import DateTime

def addSiteProperties(self, portal):
    """ adds site_properties in portal_properties """
    log_deprecated("addSiteProperties is deprecated and will be removed in "
                   "Plone 3.0")
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

def correctFolderContentsAction(actionTool):
    log_deprecated("correctFolderContentsAction is deprecated and will be "
                   "removed in Plone 3.0")
    _actions=actionTool._cloneActions()
    for action in _actions:
        if action.id=='folderContents':
            action.name=action.title='Contents'
            action.condition=Expression('object/displayContentsTab')
            action.permissions=(ListFolderContents,)
    actionTool._actions=_actions

