from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

def addYearRangeProperties(portal):
    """Add min_year/max_year properties in site_properties:

    site_properties/min_year:
       the minimun year displayed at callendar widgets
    site_properties/max_year:
       the maximun year displayed at callendar widgets
    """
    props = getToolByName(portal, 'portal_properties').site_properties
    year = DateTime().year()
    if not hasattr(props, 'min_year'):
        props._setProperty('min_year', year - 5, 'int')
    if not hasattr(props, 'max_year'):
        props._setProperty('max_year', year + 6, 'int')

def twozeroone(portal):
    """ Upgrade from Plone 2.0 to Plone 2.0.1"""
    out = []
    out.append('Adding year range properties: min_year, max_year')
    addYearRangeProperties(portal)
    return out
