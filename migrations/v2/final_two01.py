from Products.CMFCore.utils import getToolByName

def addYearRangeProperties(portal):
    """Add years range properties in site_properties:

    site_properties/calendar_starting_year: (default: 1999)
       the fixed minimun year displayed on callendar widgets
    site_properties/calendar_future_years_available: (default: 5)
       how many years (from current year) are displayed on callendar widgets
    """
    props = getToolByName(portal, 'portal_properties').site_properties
    if not hasattr(props, 'calendar_starting_year'):
        props._setProperty('calendar_starting_year', 1999, 'int')
    if not hasattr(props, 'calendar_future_years_available'):
        props._setProperty('calendar_future_years_available', 5, 'int')

def twozeroone(portal):
    """ Upgrade from Plone 2.0 to Plone 2.0.1"""
    out = []
    out.append('Adding year range properties: calendar_starting_year, '
               'calendar_future_years_available.')
    addYearRangeProperties(portal)
    return out
