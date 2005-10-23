import os
import string

import zLOG

from Products.StandardCacheManagers import AcceleratedHTTPCacheManager, RAMCacheManager
from Products.CMFDefault.Document import addDocument
from Globals import package_home
from Products.CMFPlone import cmfplone_globals
from Products.CMFCore.utils import getToolByName
from Products.CMFQuickInstallerTool import QuickInstallerTool, AlreadyInstalled
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore import CachingPolicyManager
from Products.CMFCore.DirectoryView import createDirectoryView, manage_listAvailableDirectories
from Products.CMFCore.Expression import Expression

from Products.CMFPlone.migrations.v2.plone2_base import setupExtEditor, addDocumentActions, addActionIcons
from Products.CMFPlone.migrations.migration_util import safeEditProperty, addLinesToProperty
from Products.CMFPlone.setup import ConfigurationMethods
from Products.CMFPlone import ToolNames, transaction
from portlet_migration import upgradeSlots2Portlets
import plone2_base

from Acquisition import aq_base
from ZODB.POSException import ConflictError

def oneX_twoBeta2(portal):
    """ Migrations from 1.0.x to 2.x """
    out = []

    out.append("Setting type of plone portal to 'Plone Site")
    portal._setPortalTypeName('Plone Site')

    #create the QuickInstaller
    out.append("Creating a quick installer")
    if not hasattr(portal.aq_explicit,'portal_quickinstaller'):
        portal.manage_addProduct['CMFQuickInstallerTool'].manage_addTool('CMF QuickInstaller Tool', None)
    out.append("Adding in a group user folder")
    addGroupUserFolder(portal)

    out.append("Removing deprecated portal_form_validation tool")
    if 'portal_form_validation' in portal.objectIds():
        portal.manage_delObjects('portal_form_validation')

    out.append("Setting default page values")
    props = portal.portal_properties.site_properties
    default_values = ['index_html', 'index.html', 'index.htm', 'FrontPage']
    safeEditProperty(props, 'default_page', default_values, 'lines')
    if props.hasProperty('allow_sendto'):
        props._delProperty('allow_sendto')
    addLinesToProperty(props, 'use_folder_tabs', 'Plone Site')
    if props.hasProperty('portal_factory_types'):
        props._delProperty('portal_factory_types')

    out.append("Turning on syndication")
    portal.portal_syndication.isAllowed=1 #turn syndication on

    out.append("Adding document actions")
    addDocumentActions(portal)
    out.append("Adding action icons")
    addActionIcons(portal)
    out.append("Adding cache accelerators")
    addCacheAccelerators(portal)

    out.append("Adding cache accelerators")
    if 'portal_interface' not in portal.objectIds():
        portal.manage_addProduct['CMFPlone'].manage_addTool('Portal Interface Tool')

    out.append("Altering skins to reflect plone 2 new skin paths")
    fixupPlone2SkinPaths(portal, out)
    # add portal_prefs

    out.append("Adding in a control panel")
    addControlPanel(portal)
    out.append("Upgrading with new portal factory")
    upgradePortalFactory(portal)
    updateNavigationProperties(portal)

    #Support for cropping descriptions in search results
    safeEditProperty(props,'search_results_description_length',160,'int')
    safeEditProperty(props,'ellipsis','...','string')

    #Set ext_editor property in site_properties
    setupExtEditor(portal)

    out.append("Adding in new form controller")
    addFormController(portal)

    out.append("Moving portraits into the memberdata tool")
    #migrate Memberdata, Membership and Portraits
    migrateMemberdataTool(portal)
    migratePortraits(portal)

    out.append("Moving all tools to the new Plone base classes")
    migrateTools(portal)
    out.append(("Moving some old templates out of the way, such as header and footer, since these will cause breakage", zLOG.WARNING))
    moveOldTemplates(portal)
    out.append("Updating nav tree")
    migrateNavTree(portal)
    out.append("Adding error log")
    ConfigurationMethods.addErrorLog(None, portal)
    out.append("Assigning titles to tools")
    ConfigurationMethods.assignTitles(None, portal)

    out.append(("Marking old fs directory views out-dated", zLOG.WARNING))
    deprFsViews(portal)
    removed = removeOldSkins(portal)
    out.append(("Setting default skin to Plone Default and removing old skin from portal_skins. Removed: %s" % ','.join(removed), zLOG.WARNING))

    out.append("Updating slots to portlets")
    upgradeSlots2Portlets(portal)
    out.append("Setting up calendar tool")
    plone2_base.setupCalendar(portal)
    out.append("Fixing portal_undo actions")
    fixUndoActions(portal)
    out.append("Fixing folder contents action")
    fixFolderActions(portal)
    removed = removeTranslationService(portal)
    if removed:
        out.append(("Removing deprecated translation service. Plone 2 is using the PlacelessTranslationService for translation. Your old translation data is still stored in the Localizer.", zLOG.WARNING))
    out.append('Adding plone tableless directory view')
    addPloneTableless(portal)
    return out

def doit(self):
    raise NotImplementedError, "This should be run from migrations now, we have it fixed"

def fixActionsOn(tool):
    if not hasattr(tool.aq_explicit, '_cloneActions'):
        return
    actions=tool._cloneActions()
    for a in actions:
        _action=a.action.text.split('/')
        if 'portal_form' in _action:
            _action.remove('portal_form')
        a.action=Expression('/'.join(_action))
    tool._actions=tuple(actions)

def removePortalFormFromActions(portal):
    at=getToolByName(portal, 'portal_actions')
    aps=at.action_providers
    for ap in aps:
        tool=getToolByName(portal, ap)
        fixActionsOn(tool)

    tt=getToolByName(portal, 'portal_types')
    for ptype in tt.objectValues():
        try:
            fixActionsOn(ptype)
        except ConflictError:
            raise
        except:
            print 'fixActionsOn, ', ptype.getId(), 'failed. '

def _migrate(portal, toolid, name, attrs):
    orig=getToolByName(portal, toolid)
    portal.manage_delObjects(toolid)
    portal.manage_addProduct['CMFPlone'].manage_addTool(name)
    tool = getToolByName(portal, toolid)
    for attr in attrs:
        setattr(tool, attr, aq_base(getattr(aq_base(orig), attr)))
    return aq_base(orig)

def moveOldTemplates(portal):
    #attempt to move old templates out the wway
    st = getToolByName(portal, 'portal_skins')
    custom = st.custom
    for id in custom.objectIds():
        if id in ('main_template', 'header', 'footer', 'folder_contents', 'plone.css'):
            st.custom.manage_renameObjects([id], ['premigration_'+id])

def migrateTools(portal):
    _migrate(portal, 'portal_actionicons', ToolNames.ActionIconsTool, ['_icons','_lookup'])
    _migrate(portal, 'portal_actions', ToolNames.ActionsTool, ['_actions', 'action_providers'])
    _migrate(portal, 'portal_calendar', ToolNames.CalendarTool, [])
    _migrate(portal, 'portal_registration', ToolNames.RegistrationTool, ['_actions'])
    _migrate(portal, 'portal_url', ToolNames.URLTool, ['_actions',])
    _migrate(portal, 'portal_undo', ToolNames.UndoTool, ['_actions'])
    _migrate(portal, 'portal_catalog', ToolNames.CatalogTool, ['_actions', '_catalog'])
    _migrate(portal, 'portal_metadata', ToolNames.MetadataTool, ['_actions', 'element_specs'])
    _migrate(portal, 'portal_syndication', ToolNames.SyndicationTool, [])
    _migrate(portal, 'portal_discussion', ToolNames.DiscussionTool, ['_actions'])
    _migrate(portal, 'portal_groups', ToolNames.GroupsTool, ['_actions',
        'groupworkspaces_id', 'groupWorkspacesCreationFlag',
        'groupWorkspaceType', ])
    _migrate(portal, 'portal_groupdata', ToolNames.GroupDataTool, ['_actions',
        '_members'])

    orig=_migrate(portal, 'portal_types', ToolNames.TypesTool, ['_actions', 'meta_types'])
    tt = getToolByName(portal, 'portal_types')
    for info in orig._objects:
        obj = aq_base(getattr(orig, info['id']))
        tt._setObject(info['id'], obj)

    avail_paths=manage_listAvailableDirectories()
    orig = _migrate(portal, 'portal_skins', ToolNames.SkinsTool, ['selections', '_actions'])
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
    st.default_skin = orig.default_skin

    at = getToolByName(portal, 'portal_actions')
    ap = list(at.action_providers)
    if 'portal_types' not in ap:
        ap.append('portal_types')
    if 'portal_properties' not in ap:
        ap.append('portal_properties')
    at.action_providers = tuple(ap)

def migrateNavTree(portal):
    pp=getToolByName(portal,'portal_properties')
    p = getattr(pp , 'navtree_properties', None)

    if not p:
        setupNavTreePropertySheet(pp)

    # these won't set the property... so they won't change a existing navtree
    # since it has them already, so this is pointless. What I believe we want to do
    # here is add TempFolder to the properties...

#    if not p.hasProperty('metaTypesNotToList'):
#        p._setProperty('metaTypesNotToList',['CMF Collector','CMF Collector Issue','CMF Collector Catalog','TempFolder'],'lines')
#    if not p.hasProperty('parentMetaTypesNotToQuery'):
#        p._setProperty('parentMetaTypesNotToQuery',['TempFolder'],'lines')

    # these are all new
    #if not p.hasProperty('typesForcedFolderContents'):
    #    p._setProperty('typesForcedFolderContents', [] , 'lines')
    if not p.hasProperty('bottomLevel'):
        p._setProperty('bottomLevel', 65535 , 'int')
    if not p.hasProperty('idsNotToList'):
        p._setProperty('idsNotToList', [] , 'lines')
    addLinesToProperty(p, 'metaTypesNotToList', 'TempFolder')
    addLinesToProperty(p, 'parentMetaTypesNotToQuery', 'TempFolder')
    safeEditProperty(p, 'croppingLength', 256, 'int')


def migrateMemberdataTool(portal):
    orig_md = getToolByName(portal, 'portal_memberdata')
    portal.manage_delObjects('portal_memberdata')
    portal.manage_addProduct['CMFPlone'].manage_addTool(ToolNames.MemberDataTool)

    md = getToolByName(portal, 'portal_memberdata')
    _actions = getattr(orig_md, '_actions')
    md._actions = aq_base(_actions)
    _members = getattr(orig_md, '_members')
    md._members = aq_base(_members)
    _properties = getattr(orig_md, '_properties')
    md._properties = aq_base(_properties)
    # migrate properties
    for attr in orig_md.propertyIds():
        setattr(md, attr, aq_base(getattr(aq_base(orig_md), attr)))

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

def _newDV(st, dir):
    createDirectoryView(st, os.path.join('CMFPlone', 'skins', dir))

def fixupPlone2SkinPaths(portal, out):
    st=getToolByName(portal, 'portal_skins')
    to_add=['cmf_legacy','plone_portlets', 'plone_form_scripts', 'plone_prefs']
    for item in to_add:
        if item not in portal.portal_skins.objectIds():
            _newDV(st, item)

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
                try:
                    path.insert(path.index('plone_forms'), new)
                except ValueError:
                    out.append(("No path plone_forms was found, so couldn't add %s into skin %s" % (new, skin), zLOG.ERROR))
        st.addSkinSelection(skin, ','.join(path))
    return out

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
    transaction.commit(1)

    qi=getToolByName(portal, 'portal_quickinstaller')
    addGRUFTool=portal.manage_addProduct['GroupUserFolder'].manage_addTool
    if "portal_groups" not in portal.objectIds():
        qi.installProduct('GroupUserFolder', locked=1)
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
        qi.installProduct('CMFFormController', locked=1)
    except AlreadyInstalled:
        qi.notifyInstalled('CMFFormController') #Portal.py got to it first

def addActionIcons(portal):
    """ After installing QuickInstaller.  We must commit(1) a subtrnx
        so that we will be able to addActionIcons() to the tool
    """
    try:
        qi=getToolByName(portal, 'portal_quickinstaller')
        qi.installProduct('CMFActionIcons', locked=1)
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
                 'string:$object_url/external_edit',
                 "python: hasattr(portal.portal_properties.site_properties, 'ext_editor') and portal.portal_properties.site_properties.ext_editor and object.absolute_url() != portal_url",
                 'Modify portal content',
                 'document_actions')

    at.addAction('rss',
                 'RSS feed of this folder\'s contents',
                 'string:$object_url/RSS',
                 'python:portal.portal_syndication.isSyndicationAllowed(object)',
                 'View',
                 'document_actions')

    at.addAction('sendto',
                 'Send this page to somebody',
                 'string:$object_url/portal_form/sendto_form',
                 '',
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

def deprFsViews(portal):
    st = getToolByName(portal, 'portal_skins')
    fsViewIds = ['Images', 'actionicons', 'calendar', 'content', 'control',
        'generic', 'no_css', 'nouvelle', 'topic', 'zpt_calendar', 'zpt_content',
        'zpt_control', 'zpt_generic', 'zpt_topic',
        ]
    for fsViewId in fsViewIds:
        view = getattr(st, fsViewId, None)
        if view:
            view.title += 'Deprecated, can safely be deleted'

    for skin in st.getSkinSelections():
        oldpath = st.getSkinPath(skin)
        oldpath = [p.strip() for p in oldpath.split(',')]
        # all non depr pathes
        newpath = [p for p in oldpath if p not in fsViewIds and p != 'cmf_legacy' ]
        # all depr pathes that are in oldpath
        deprpath = [p for p in oldpath if p in fsViewIds ]
        # add depr pathes to the end after cmf_legacy
        newpath.append('cmf_legacy')
        newpath.extend(deprpath)
        # remove all plone_styles/ subdirs
        newpath = [ p for p in newpath if not p.startswith('plone_styles/') ]

        path = ','.join(newpath)
        st.addSkinSelection(skin, path)

def removeOldSkins(portal):
    st = getToolByName(portal, 'portal_skins')
    st.default_skin = 'Plone Default'
    removed = []
    skins = ['Plone Autumn', 'Plone Core', 'Plone Core Inverted',
             'Plone Corporate', 'Plone Greensleeves', 'Plone Kitty',
             'Plone Mozilla', 'Plone Mozilla New', 'Plone Prime',
             'Plone Zed', ]
    skinList = st._getSelections()
    for skin in skins:
        if skinList.has_key(skin):
            del skinList[skin]
            removed.append(skin)
    return removed

def fixUndoActions(portal):
    st = getToolByName(portal, 'portal_undo')
    # remove old actions
    for action in st._actions:
        if action.id in ('undo',):
            del action
    st.addAction('undo',
                 'Undo',
                 'string: ${portal_url}/undo_form',
                 'member',
                 'List undoable changes',
                 'user')

def fixFolderActions(portal):
    st = getToolByName(portal, 'portal_actions')
    for action in st._actions:
        if action.id == 'folderContents':
            action.visible = 1

def removeTranslationService(portal):
    """remove old translation service
    """
    ts = 'translation_service'
    if hasattr(portal.aq_explicit, ts):
        portal.manage_delObjects(ts)
        return 1

def addPloneTableless(portal):
    st = getToolByName(portal, 'portal_skins')
    if not hasattr(aq_base(st), 'plone_tableless'):
        _newDV(st, 'plone_tableless')

def registerMigrations():
    MigrationTool.registerUpgradePath('1.0.1','1.1alpha2',upg_1_0_1_to_1_1)
    MigrationTool.registerUpgradePath('1.0.2','1.1alpha2',upg_1_0_1_to_1_1)
    MigrationTool.registerUpgradePath('1.0.3','1.1alpha2',upg_1_0_1_to_1_1)

if __name__=='__main__':
    registerMigrations()
