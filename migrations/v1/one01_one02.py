from Products.CMFPlone import MigrationTool
from Products.CMFCore.utils import getToolByName

def onezerotwo(portal):
    """ Upgrade from Plone 1.0.1 to Plone 1.0.2"""
    #set up cookie crumbler
    cookie_authentication = getToolByName(portal, 'cookie_authentication')
    cookie_authentication._updateProperty('auto_login_page', 'require_login')

def registerMigrations():
    MigrationTool.registerUpgradePath(
            '1.0.1',
            '1.0.2',
            onezerotwo
            )

if __name__=='__main__':
    registerMigrations()
