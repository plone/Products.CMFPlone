from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions

def onezerotwo(portal):
    """ Upgrade from Plone 1.0.1 to Plone 1.0.2"""
    #set up cookie crumbler
    cookie_authentication = getToolByName(portal, 'cookie_authentication')
    cookie_authentication._updateProperty('auto_login_page', 'require_login')
    portal.portal_syndication.isAllowed=1

    # give Owner the right to manage local roles
    portal.manage_permission(CMFCorePermissions.ChangePermissions, ('Owner','Manager',), acquire=1)


if __name__=='__main__':
    registerMigrations()

