import os
import string
from Products.StandardCacheManagers import AcceleratedHTTPCacheManager, RAMCacheManager
from Products.CMFDefault.Document import addDocument
from Globals import package_home
from Products.CMFPlone import cmfplone_globals
from Products.CMFCore.utils import getToolByName
from Products.CMFQuickInstallerTool import QuickInstallerTool, AlreadyInstalled
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore import CachingPolicyManager
from Products.CMFCore.DirectoryView import createDirectoryView, manage_listAvailableDirectories

from Products.CMFPlone.migrations.plone2_base import setupExtEditor
from Products.CMFPlone.migrations.migration_util import safeEditProperty
from Products.CMFPlone import ToolNames

from Acquisition import aq_base

def oneX_twoBeta2(portal):
    """ Migrations from 1.0.x to 2.x """
    #create the QuickInstaller
    if not hasattr(portal.aq_explicit,'portal_quickinstaller'):
        portal.manage_addProduct['CMFQuickInstallerTool'].manage_addTool('CMF QuickInstaller Tool', None)
    addGroupUserFolder(portal)

    if 'portal_form_validation' in portal.objectIds():
        portal.manage_delObjects('portal_form_validation')

    props = portal.portal_properties.site_properties
    default_values = ['index_html', 'index.html', 'index.htm', 'FrontPage']
    safeEditProperty(props, 'default_page', default_values, 'lines')
    portal.portal_syndication.isAllowed=1 #turn syndication on

    addDocumentActions(portal)
    addActionIcons(portal)
    addCacheAccelerators(portal)

    #XXX TODO:migrate to add simple workflow
    # change the action in portal_types for viewing a folder

    if 'portal_interface' not in portal.objectIds():
        portal.manage_addProduct['CMFPlone'].manage_addTool('Portal Interface Tool')

    fixupPlone2SkinPaths(portal)
    # add portal_prefs

    addControlPanel(portal)
    upgradePortalFactory(portal)
    updateNavigationProperties(portal)

    #Support for cropping descriptions in search results
    safeEditProperty(props,'search_results_description_length',160,'int')
    safeEditProperty(props,'ellipsis','...','string')

    #Set ext_editor property in site_properties
    setupExtEditor(portal)

    addFormController(portal)

    #migrate Memberdata, Membership and Portraits
    migrateMemberdataTool(portal)
    migratePortraits(portal)

    migrateTools(portal)

def doit(self):
    oneX_twoBeta2(self)
    swapPortalRoot(self)

def swap(self):
    swapPortalRoot(self)

def _migrate(portal, toolid, name, attrs):
    from copy import deepcopy
    orig=getToolByName(portal, toolid)
    portal.manage_delObjects(toolid)
    portal.manage_addProduct['CMFPlone'].manage_addTool(name)
    tool = getToolByName(portal, toolid)
    for attr in attrs:
            setattr(tool, attr, aq_base(getattr(aq_base(orig), attr)))
    return orig

def swapPortalRoot(portal):
    """ We want to swap CMFDefault.PortalObject.Portal with CMFPlone.Portal.Portal """
    from Products.CMFPlone.Portal import PloneSite
    from StringIO import StringIO
    if portal.meta_type=='Plone Site':
        return

    parent=portal.getParentNode()
    id = portal.getId()
    old = portal

    #parent.manage_delObjects(id)
    parent._delOb(id)
    parent._setOb(id, PloneSite(id, portal.Title()))
    portal=parent[id]

    # copy ObjectManager values
    # NOTE: Collector items seem to crap so we catch their exceptions
    #       We need to reindex Collector's catalog after we _setObject
    for id, ob in old.objectItems():
        try:
            portal._setObject(id, aq_base(ob))   #copy ObjectManager values
        except Exception, e:
            pass #StringIO.write(str(e))

  
    #copy PropertManager values
    for prop in old._properties:
        propid = prop['id']
        if not portal.hasProperty(propid):
            portal.manage_addProperty(propid, old.getProperty(propid), prop['type'])

    #copy Roles
    portal.__ac_roles__=old.__ac_roles__

    #copy Security settings
    for permission in [perm for perm in dir(portal) if perm.endswith('_Permission')]:
        setattr(portal, permission, getattr(old, permission))

    #copy workflow
    if hasattr(aq_base(old), 'workflow_history'):
        setattr(portal, 'workflow_history', aq_base(old))

    #We have a portal_type for Plone objects, Plone Site
    #It has no workflow associate with it.
    portal.portal_types.manage_addTypeInformation(FactoryTypeInformation.meta_type,
                                    id='Plone Site',
                                    typeinfo_name='CMFPlone: Plone Site')
    portal._setPortalTypeName('Plone Site')
    portal.portal_workflow._chains_by_type['Plone Site']=()

    #lastly give it new icon
    portal.icon='misc_/CMFPlone/tool.gif'
    return portal 


def migrateTools(portal):
    _migrate(portal, 'portal_actionicons', ToolNames.ActionIconsTool, ['_icons'])
    _migrate(portal, 'portal_actions', ToolNames.ActionsTool, ['_actions', 'action_providers'])
    _migrate(portal, 'portal_calendar', ToolNames.CalendarTool, [])
    _migrate(portal, 'portal_registration', ToolNames.RegistrationTool, ['_actions'])
    _migrate(portal, 'portal_url', ToolNames.URLTool, ['_actions',])
    _migrate(portal, 'portal_undo', ToolNames.UndoTool, ['_actions'])
    _migrate(portal, 'portal_catalog', ToolNames.CatalogTool, ['_actions', '_catalog'])
    _migrate(portal, 'portal_metadata', ToolNames.MetadataTool, ['_actions', 'element_specs'])
    _migrate(portal, 'portal_syndication', ToolNames.SyndicationTool, [])

    orig=_migrate(portal, 'portal_types', ToolNames.TypesTool, ['_actions', 'meta_types']) #XXX
    tt = getToolByName(portal, 'portal_types')
    for info in orig._objects:
        obj = aq_base(getattr(orig, info['id']))
        tt._setObject(info['id'], obj)

    avail_paths=manage_listAvailableDirectories()
    orig = _migrate(portal, 'portal_skins', ToolNames.SkinsTool, ['selections', '_actions']) #XXX
    st = getToolByName(portal, 'portal_skins')
    for info in orig._objects:
        obj = aq_base(getattr(orig, info['id']))
        if obj.meta_type=='Filesystem Directory View' and \
           obj.id not in st.objectIds():
            for avail in avail_paths:
                if obj._dirpath.endswith(avail):
                    createDirectoryView(st, avail, obj.id)
        else:
            if obj.meta_type!='Filesystem Directory View':
                st._setObject(info['id'], obj)
    st.request_varname = orig.request_varname

    at = getToolByName(portal, 'portal_actions')
    ap = list(at.action_providers)
    if 'portal_types' not in ap:
        ap.append('portal_types')
    if 'portal_properties' not in ap:
        ap.append('portal_properties')
    at.action_providers = tuple(ap)

def migrateMemberdataTool(portal):
    orig_md = getToolByName(portal, 'portal_memberdata')
    portal.manage_delObjects('portal_memberdata')
    portal.manage_addProduct['CMFPlone'].manage_addTool(ToolNames.MemberDataTool)

    md = getToolByName(portal, 'portal_memberdata')
    _actions = getattr(orig_md, '_actions')
    md._actions = aq_base(_actions)
    _members = getattr(orig_md, '_members')
    md._members = aq_base(_members)
   

PORTRAIT_ID='MyPortrait'
def migratePortraits(portal):
    from StringIO import StringIO
    mt = getToolByName(portal, 'portal_membership')
    acl_users = getToolByName(portal, 'acl_users')
    
    for id in mt.listMemberIds():
        personal=mt.getPersonalFolder(id)
        if personal and PORTRAIT_ID in personal.objectIds():
            portrait=getattr(personal, PORTRAIT_ID)
            buf = StringIO(portrait.data)
            buf.filename=PORTRAIT_ID
            buf.seek(0) #lovely Zope mixing OFS interfaces w/ HTTP interfaces
            mt.changeMemberPortrait(buf, id)
        
def fixupPlone2SkinPaths(portal):
    def newDV(st, dir):
        from os import path
        createDirectoryView(st, path.join('CMFPlone', 'skins', dir))

    st=getToolByName(portal, 'portal_skins')
    to_add=['cmf_legacy','plone_portlets', 'plone_form_scripts', 'plone_prefs']
    for item in to_add:
        newDV(st, item)

    to_remove=['plone_templates/ui_slots', 'plone_scripts/form_scripts', 
               'plone_3rdParty/CMFCollector', 'plone_3rdParty/CMFCalendar']
    skins = st.getSkinSelections()
    for skin in skins:
        path = st.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        for old in to_remove:
            if old in path: 
                path.remove(old)
        for new in to_add:
            if new not in path:
                path.insert(path.index('plone_forms'), new)
        st.addSkinSelection(skin, ','.join(path))

def upgradePortalFactory(portal):
    site_props = portal.portal_properties.site_properties
    if not hasattr(site_props,'portal_factory_types'):
        site_props._setProperty('portal_factory_types',('',), 'lines')

    typesTool = getToolByName(portal, 'portal_types')
    # add temporary folder type for portal_factory
    if not hasattr(typesTool, 'TempFolder'):
        typesTool.manage_addTypeInformation(FactoryTypeInformation.meta_type,
                                             id='TempFolder',
                                             typeinfo_name='CMFCore: Portal Folder')
        folder = typesTool.Folder
        tempfolder = typesTool.TempFolder
        tempfolder.content_meta_type='TempFolder'
        tempfolder.icon = folder.icon
        tempfolder.global_allow = 0  # make TempFolder not implicitly addable
        tempfolder.allowed_content_types=(typesTool.listContentTypes())


def addControlPanel(portal):
    from Products.CMFPlone.ToolNames import ControlPanelTool
    addPloneTool=portal.manage_addProduct['CMFPlone'].manage_addTool
    if not hasattr(portal.aq_explicit,'portal_controlpanel'):
        addPloneTool(ControlPanelTool, None)
    # must be done here because controlpanel depends on
    # portal_actionicons concerning icon registration
    portal.portal_controlpanel.registerDefaultConfiglets()


def addCacheAccelerators(portal):
    # add in caches, HTTPCache and RamCache
    meta_type = AcceleratedHTTPCacheManager.AcceleratedHTTPCacheManager.meta_type
    if 'HTTPCache' not in portal.objectIds(meta_type):
        AcceleratedHTTPCacheManager.manage_addAcceleratedHTTPCacheManager(portal, 'HTTPCache')
    meta_type = RAMCacheManager.RAMCacheManager.meta_type
    if 'RAMCache' not in portal.objectIds(meta_type):
        RAMCacheManager.manage_addRAMCacheManager(portal, 'RAMCache')
    if 'caching_policy_manager' not in portal.objectIds():
        CachingPolicyManager.manage_addCachingPolicyManager(portal)


def addGroupUserFolder(portal):
    """ We _must_ commit() here.  Because the Portal does not really exist in
        the ZODB.  And the acl_users object we are moving *must* have a _p_jar
        attribute.  We get the Connection object by commit()ing.

        NOTE: In the Install routine for GRUF it does a subtransaction commit()
        so that you can manipulate the acl_users folders.
    """
    get_transaction().commit(1)

    qi=getToolByName(portal, 'portal_quickinstaller')
    qi.installProduct('GroupUserFolder')
    addGRUFTool=portal.manage_addProduct['GroupUserFolder'].manage_addTool
    addGRUFTool('CMF Groups Tool')
    addGRUFTool('CMF Group Data Tool')

def setupHelpSection(portal):
    # create and populate the 'plone_help' folder in the root of the plone
    # the contents are STX files in CMFPlone/docs
    if 'plone_help' not in portal.objectIds():
        portal.invokeFactory(type_name='Folder', id='plone_help')
        plone_help=portal.plone_help
        docs_path=os.path.join(package_home(cmfplone_globals), 'help')
        for filename in os.listdir(docs_path):
            _path=os.path.join(docs_path, filename)
            if not os.path.isdir(_path):
                doc=open(_path, 'r')
                addDocument(plone_help, filename, filename, '',
                            'structured-text', doc.read())
                getattr(plone_help,filename)._setPortalTypeName('Document')

def addFormController(portal):
    """ """
    try:
        qi=getToolByName(portal, 'portal_quickinstaller')
        qi.installProduct('CMFFormController')
    except AlreadyInstalled:
        qi.notifyInstalled('CMFFormController') #Portal.py got to it first

def addActionIcons(portal):
    """ After installing QuickInstaller.  We must commit(1) a subtrnx
        so that we will be able to addActionIcons() to the tool
    """
    try:
        qi=getToolByName(portal, 'portal_quickinstaller')
        qi.installProduct('CMFActionIcons')
    except AlreadyInstalled:
        qi.notifyInstalled('CMFActionIcons') #Portal.py got to it first

    ai=getToolByName(portal, 'portal_actionicons')
    ai.addActionIcon('plone', 'sendto', 'mail_icon.gif', 'Send-to')
    ai.addActionIcon('plone', 'print', 'print_icon.gif', 'Print')
    ai.addActionIcon('plone', 'rss', 'rss.gif', 'Syndication')
    ai.addActionIcon('plone', 'extedit', 'extedit_icon.gif', 'ExternalEdit')

def addDocumentActions(portal):
    at = portal.portal_actions

    at.addAction('extedit',
                 'Edit this file in an external application (Requires Zope ExternalEditor installed)',
                 'string:${object_url}/external_edit',
                 "python: hasattr(portal.portal_properties.site_properties, 'ext_editor') and portal.portal_properties.site_properties.ext_editor and object.absolute_url() != portal_url",
                 'Modify portal content',
                 'document_actions')

    at.addAction('rss',
                 'RSS feed of this folder\'s contents',
                 'string:${object_url}/RSS',
                 'python:portal.portal_syndication.isSyndicationAllowed(object)',
                 'View',
                 'document_actions')

    at.addAction('sendto',
                 'Send this page to somebody',
                 'string:${object_url}/portal_form/sendto_form',
                 "python:hasattr(portal.portal_properties.site_properties, 'allow_sendto')",
                 'View',
                 'document_actions')

    at.addAction('print',
                 'Print this page',
                 'string:javascript:this.print();',
                 '',
                 'View',
                 'document_actions')

def updateNavigationProperties(portal):
    nav_props = portal.portal_properties.navigation_properties
    nav = (('default.reconfig.success', 'url:plone_control_panel'),
           )
    for id, action in nav:
        if nav_props.hasProperty(id):
            nav_props._updateProperty(id, action)
        else:
            nav_props._setProperty(id, action)

def registerMigrations():
    MigrationTool.registerUpgradePath('1.0.1','1.1alpha2',upg_1_0_1_to_1_1)
    MigrationTool.registerUpgradePath('1.0.2','1.1alpha2',upg_1_0_1_to_1_1)
    MigrationTool.registerUpgradePath('1.0.3','1.1alpha2',upg_1_0_1_to_1_1)

if __name__=='__main__':
    registerMigrations()
