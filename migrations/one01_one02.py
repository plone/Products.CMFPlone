from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions

def onezerotwo(portal):
    """ Upgrade from Plone 1.0.1 to Plone 1.0.2"""
    #set up cookie crumbler
    cookie_authentication = getToolByName(portal, 'cookie_authentication')
    cookie_authentication._updateProperty('auto_login_page', 'require_login')
    portal.portal_syndication.isAllowed=1

    #fix badly titled action
    at=getToolByName(portal, 'portal_actions')
    at_actions=at._cloneActions()
    for a in at_actions:
        if a.id=='folderContents' and a.category=='folder':
            a.title='Folder Contents'
    at._actions=at_actions

if __name__=='__main__':
    registerMigrations()

