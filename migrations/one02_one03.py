from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions

def onezerothree(portal):
    """ Upgrade from Plone 1.0.2 to Plone 1.0.3"""
    sprops=portal.portal_properties.site_properties
    sprops.manage_addProperty('invalid_ids', ('actions',), 'lines')

if __name__=='__main__':
    registerMigrations()

