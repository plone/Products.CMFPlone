from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions

def onezerofour(portal):
    """ Upgrade from Plone 1.0.3 to Plone 1.0.4"""
    props=getToolByName(portal, 'portal_properties')
    sprops=getattr(props,'site_properties')
            
if __name__=='__main__':
    registerMigrations()