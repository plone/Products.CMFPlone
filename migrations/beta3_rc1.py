from Products.CMFPlone import MigrationTool
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFCore import CMFCorePermissions

def threerc1(portal):
    """ Upgrade from Plone 1.0 Beta 3 to RC 1 """

    #adding navigation properties
    nav_tool=portal.portal_navigation
    nav_tool.addTransitionFor('default', 'createObject', 'success_no_edit', 'action:view')

    # these were missed in the initial beta 3 release
    if not nav_tool.hasProperty('default.folder_rename_form.failure'):
        nav_tool.addTransitionFor('default', 'folder_rename_form', 'failure', 'folder_rename_form')
    if not nav_tool.hasProperty('default.folder_rename_form.success'):
        nav_tool.addTransitionFor('default', 'folder_rename_form', 'success', 'script:folder_rename')
    if not nav_tool.hasProperty('default.register.failure'):
        nav_tool.addTransitionFor('default', 'register', 'failure', 'join_form')

    props = portal.portal_properties.site_properties
    if not hasattr(props, 'allowRolesToAddKeywords'):
        props._setProperty('allowRolesToAddKeywords', ['Manager', 'Reviewer'], 'lines')

    if not portal.portal_memberdata.hasProperty('fullname'):
       portal.portal_memberdata.manage_addProperty('fullname', '', 'string')
