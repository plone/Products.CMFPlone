from migration_utils import safeEditProperty

def upg_1_0_1_to_1_1(portal):
    """ Migrations from 1.0.1 to 1.1 """
    props = portal.portal_properties.site_properties
    default_values = ['index_html', 'index.html', 'index.htm']
    safeEditProperty(props, 'default_page', default_values, 'lines')

    # migrate to GRUF here

    # migrate to add simple workflow

    # change the action in portal_types for
    # viewing a folder

    
    
