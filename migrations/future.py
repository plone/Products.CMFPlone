from migration_utils import safeEditProperty

def future(portal):
    """ Future migrations """
    props = portal.portal_properties.site_properties
    default_values = ['index_html', 'index.html', 'index.htm']
    safeEditProperty(props, 'default_page', default_values, 'lines')
    