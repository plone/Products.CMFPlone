from migration_util import safeEditProperty
from Products.StandardCacheManagers import AcceleratedHTTPCacheManager, RAMCacheManager

def upg_1_0_1_to_1_1(portal):
    """ Migrations from 1.0.1 to 1.1 """
    props = portal.portal_properties.site_properties
    default_values = ['index_html', 'index.html', 'index.htm']
    safeEditProperty(props, 'default_page', default_values, 'lines')

    #add action->icon mapping propertysheet in portal_properties
    at = portal.portal_actions

    at.addAction('sendto','Send this page to somebody','string:${object_url}/portal_form/sendto_form',
                 "python:hasattr(portal.portal_properties.site_properties,'allow_sendto')",'View','document_actions')
    at.addAction('print', 'Print this page', 'string:javascript:this.print();', '', 'View', 'document_actions')
    at.addAction('rss', 'RSS Feed of this folders contents', 'string:${object_url}/RSS',
                'python:portal.portal_syndication.isSyndicationAllowed(object)', 'View', 'document_actions')

    props = portal.portal_properties
    if 'action_to_icon_mapping' not in props.objectIds():
        props.manage_addPropertySheet('action_to_icon_mapping', 'Maps documentActions to Icons')
    p = props.action_to_icon_mapping
    p._setProperty('document_actions.sendto', 'mail_icon.gif', 'string')
    p._setProperty('document_actions.print', 'print_icon.gif', 'string')
    p._setProperty('document_actions.rss', 'xml.gif', 'string')

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

def registerMigrations():
    MigrationTool.registerUpgradePath(
            '1.0.1',
            '1.1',
            upg_1_0_1_to_1_1
            )

if __name__=='__main__':
    registerMigrations()
