from migration_util import safeEditProperty
from Products.StandardCacheManagers import AcceleratedHTTPCacheManager, RAMCacheManager
from Products.CMFDefault.Document import addDocument
from Globals import package_home
from Products.CMFPlone import cmfplone_globals
from Products.CMFQuickInstallerTool import QuickInstallerTool
import os


def upg_1_0_1_to_1_1(portal):
    """ Migrations from 1.0.1 to 1.1 """

    #create the QuickInstaller
    if not hasattr(portal.aq_explicit,'portal_quickinstaller'):
        portal.manage_addProduct['CMFQuickInstallerTool'].manage_addTool('CMF QuickInstaller Tool', None)

    props = portal.portal_properties.site_properties
    default_values = ['index_html', 'index.html', 'index.htm']
    safeEditProperty(props, 'default_page', default_values, 'lines')

    #add action->icon mapping propertysheet in portal_properties
    at = portal.portal_actions

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
    at.addAction('rss',
                 'RSS Feed of this folders contents',
                 'string:${object_url}/RSS',
                 'python:portal.portal_syndication.isSyndicationAllowed(object)',
                 'View',
                 'document_actions')
    
    # trashcan, Maik
    pm = portal.portal_membership
    pm.addAction('mytrashcan',
        'My Trashcan',
        'string:${portal/portal_membership/getHomeUrl}/.trashcan/folder_contents',
        'python:member and hasattr(portal.portal_membership.getHomeFolder(), ".trashcan")',
        'View',
        'user')
        
    #Install CMFActionIcons and Plone action icons
    portal.portal_quickinstaller.installProduct('CMFActionIcons')
    get_transaction().commit(1)

    actionicons=portal.portal_actionicons
    actionicons.addActionIcon('plone', 'sendto', 'mail_icon.gif', 'Send-to')
    actionicons.addActionIcon('plone', 'print', 'print_icon.gif', 'Print')
    actionicons.addActionIcon('plone', 'rss', 'xml.gif', 'Syndication')

    portal.portal_syndication.isAllowed=1 #turn syndication on

    # migrate to GRUF here

    # migrate to add simple workflow

    # change the action in portal_types for
    # viewing a folder

    # add in caches, HTTPCache and RamCache
    meta_type = AcceleratedHTTPCacheManager.AcceleratedHTTPCacheManager.meta_type
    if 'HTTPCache' not in portal.objectIds(meta_type):
        AcceleratedHTTPCacheManager.manage_addAcceleratedHTTPCacheManager(portal, 'HTTPCache')

    meta_type = RAMCacheManager.RAMCacheManager.meta_type
    if 'RAMCache' not in portal.objectIds(meta_type):
        RAMCacheManager.manage_addRAMCacheManager(portal, 'RAMCache')

    # create portal_interface tool.
    if 'portal_interface' not in portal.objectIds():
        portal.manage_addProduct['CMFPlone'].manage_addTool('Portal Interface Tool')

    #create the PloneControlPanel if not present
    addPloneTool=portal.manage_addProduct['CMFPlone'].manage_addTool
    if not hasattr(portal.aq_explicit,'portal_configuration'):
        addPloneTool('Plone Control Panel', None)

    # must be done here because controlpanel depends on
    # portal_actionicons concerning icon registration
    portal.portal_configuration.registerDefaultConfiglets()
    
def registerMigrations():
    MigrationTool.registerUpgradePath(
            '1.0.1',
            '1.1',
            upg_1_0_1_to_1_1
            )

if __name__=='__main__':
    registerMigrations()
