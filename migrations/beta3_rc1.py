from Products.CMFPlone import MigrationTool
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFCore import CMFCorePermissions

def threerc1(portal):
    """ Upgrade from Plone 1.0 Beta 3 to RC 1 """

    #adding navigation properties
    nav_tool=portal.portal_navigation
    nav_tool.addTransitionFor('default', 'createObject', 'success_no_edit', 'action:view')

    # these were missed in the initial beta 3 release
    nav_tool.addTransitionFor('default', 'folder_rename_form', 'failure', 'folder_rename_form')
    nav_tool.addTransitionFor('default', 'folder_rename_form', 'success', 'script:folder_rename_form')
    nav_tool.addTransitionFor('default', 'register', 'failure', 'join_form')

def registerMigrations():
    # so the basic concepts is you put a bunch of migrations is here
    MigrationTool.registerUpgradePath(
            '1.0beta3', 
            '1.0rc1', 
            threerc1
            )
    # it will run through them all until its upto date
    # etc
    # MigrationTool.registerUpgradePath('1.0beta3', '1.0beta4', beta3two4)

if __name__=='__main__':
    registerMigrations()

