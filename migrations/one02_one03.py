from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions

def onezerothree(portal):
    """ Upgrade from Plone 1.0.2 to Plone 1.0.3"""
    props=getToolByName(portal, 'portal_properties')
    sprops=getattr(props,'site_properties')
    if sprops is not None:
        if not sprops.hasProperty('invalid_ids'):
            sprops.manage_addProperty('invalid_ids', ('actions',), 'lines')

if __name__=='__main__':
    registerMigrations()

