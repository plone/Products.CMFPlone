import os
import string
from migration_util import safeEditProperty
from Products.StandardCacheManagers import AcceleratedHTTPCacheManager, RAMCacheManager
from Products.CMFDefault.Document import addDocument
from Globals import package_home
from Products.CMFPlone import cmfplone_globals
from Products.CMFCore.utils import getToolByName
from Products.CMFQuickInstallerTool import QuickInstallerTool, AlreadyInstalled
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore import CachingPolicyManager
from plone2_base import setupExtEditor

def oneX_twoBeta2(portal):
    """ Migrations from 1.0.x to 2.x """
    #create the QuickInstaller
    if not hasattr(portal.aq_explicit,'portal_quickinstaller'):
        portal.manage_addProduct['CMFQuickInstallerTool'].manage_addTool('CMF QuickInstaller Tool', None)
    addGroupUserFolder(portal)

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

    # add portal_prefs
    skinsTool = getToolByName(self, "portal_skins")
    skins = skinsTool.getSkinSelections()
    for skin in skins:
        path = skinsTool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        if 'plone_prefs' not in path:
            path.insert(path.index('plone_forms'), 'plone_prefs')
            path = string.join(path, ', ')
            skinsTool.addSkinSelection(skin, path)

    addControlPanel(portal)
    upgradePortalFactory(portal)
    updateNavigationProperties(portal)

    #Support for cropping descriptions in search results
    safeEditProperty(props,'search_results_description_length',160,'int')
    safeEditProperty(props,'ellipsis','...','string')

    #Set ext_editor property in site_properties
    setupExtEditor(portal)

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
    addPloneTool=portal.manage_addProduct['CMFPlone'].manage_addTool
    if not hasattr(portal.aq_explicit,'portal_control_panel_actions'):
        addPloneTool('Plone Control Panel', None)
    # must be done here because controlpanel depends on
    # portal_actionicons concerning icon registration
    portal.portal_control_panel_actions.registerDefaultConfiglets()


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
