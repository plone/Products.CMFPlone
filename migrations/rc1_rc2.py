from Products.CMFPlone import MigrationTool
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFCore import CMFCorePermissions

def rc1rc2(portal):
    """ Upgrade from Plone 1.0 RC1 to RC1 """

    #adding navigation properties
    nav_tool=portal.portal_navigation
    nav_tool._setProperty('default.folder_rename_form.success', 'script:folder_rename')

def registerMigrations():
    # so the basic concepts is you put a bunch of migrations is here
    MigrationTool.registerUpgradePath(
            '1.0RC1', 
            '1.0RC2', 
            rc1rc2
            )
if __name__=='__main__':
    registerMigrations()

