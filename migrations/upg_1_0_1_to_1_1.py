from migration_util import safeEditProperty
from Products.StandardCacheManagers import AcceleratedHTTPCacheManager, RAMCacheManager

def upg_1_0_1_to_1_1(portal):
    """ Migrations from 1.0.1 to 1.1 """
    props = portal.portal_properties.site_properties
    default_values = ['index_html', 'index.html', 'index.htm']
    safeEditProperty(props, 'default_page', default_values, 'lines')

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
    
