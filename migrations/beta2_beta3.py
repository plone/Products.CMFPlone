from Products.CMFPlone import MigrationTool
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFCore import CMFCorePermissions

def twothree(portal):
    """ Upgrade from Plone 1.0 Beta 2 to Beta 3 """
    typesTool = portal.portal_types
    # lines 78
    # register Btree folder if aint there
    try:
        typesTool.manage_addTypeInformation('Factory-based Type Information',
                                            'BTree Folder', 
                                            'BTreeFolder2: CMF BTree Folder')
    # ugh, this is bad                                            
    except:
        pass
    
    # line 148
    # portal workflow change
    wf_tool=portal.portal_workflow
    folder_wf = wf_tool['folder_workflow']
    folder_wf.states.visible.permission_roles[CMFCorePermissions.ListFolderContents]=['Manager', 'Owner']

    # line 223
    # some additions to validators
    form_tool = portal.portal_form
    form_tool.setValidators('folder_rename_form', ['validate_folder_rename'])
    form_tool.setValidators('sendto_form', ['validate_sendto'])

    # line 251
    # add columns to the calatog 
    catalog = portal.portal_catalog
    if not catalog._catalog.schema.has_key('getId'):
        catalog.addColumn('getId', None)
    if not catalog._catalog.schema.has_key('meta_type'):
        catalog.addColumn('meta_type', None)

    # line 195
    # add in site properties sheet
    
    #moving properties from CMF Site object to portal_properties/site_properties
    policy=DefaultCustomizationPolicy()
    policy.addSiteProperties(portal)       
    
    prop_tool = portal.portal_properties
    if 'site_properties' not in prop_tool.objectIds():
        prop_tool.manage_addPropertySheet('site_properties', 'Site Properties')

    p = prop_tool.site_properties
    
    # line 195
    # add in auth cookie length
    _ids = p.propertyIds()
    if 'auth_cookie_length' not in _ids:
        p._setProperty('auth_cookie_length', 0, 'int')
    # line 110
    if 'allow_sendto' not in _ids:
        p._setProperty('allow_sendto', 0, 'boolean')
    if 'enable_navigation_logging' not in _ids:
        p._setProperty('enable_navigation_logging', 0, 'boolean')
    # /adding
    #below was added thanks to interra issue #659
    if 'email_from_address' not in _ids:
        p._setProperty('email_from_address', '', 'string')
    if 'email_from_name' not in _ids:
        p._setProperty('email_from_name', '', 'string')
    if 'validate_email' not in _ids:
        p._setProperty('validate_email', 0, 'boolean')
    if 'allowAnonymousViewAbout' not in _ids:
        p._setProperty('allowAnonymousViewAbout', 1, 'boolean')
    if 'localTimeFormat' not in _ids:
        p._setProperty('localTimeFormat', '%Y-%m-%d', 'string')
    if 'localLongTimeFormat' not in _ids:
        p._setProperty('localLongTimeFormat', '%Y-%m-%d %I:%M %p', 'string')
    if 'default_language' not in _ids:
        p._setProperty('default_language', 'en', 'string')
    if 'default_charset' not in _ids:
        p._setProperty('default_charset', 'iso-8859-1', 'string')
    if 'use_folder_tabs' not in _ids:
        p._setProperty('use_folder_tabs', ['Folder',], 'lines')
    if 'ext_editor' not in _ids:
        p._setProperty('ext_editor', 0, 'boolean')
    if 'available_editors' not in _ids:
        p._setProperty('available_editors', [], 'lines')

    #adding navigation properties
    nav_tool=portal.portal_navigation
    nav_tool.addTransitionFor('default', 'createObject', 'success', 'action:edit')
    nav_tool.addTransitionFor('default', 'sendto_form', 'success', 'script:sendto')
    nav_tool.addTransitionFor('default', 'sendto_form', 'failure', 'sendto_form')
    nav_tool.addTransitionFor('default', 'sendto', 'success', 'action:view')
    nav_tool.addTransitionFor('default', 'sendto', 'failure', 'action:view')
    # these were missed in the initial beta 3 release
    nav_tool.addTransitionFor('default', 'folder_rename_form', 'failure', 'folder_rename_form')
    nav_tool.addTransitionFor('default', 'folder_rename_form', 'success', 'script:folder_rename')
    nav_tool.addTransitionFor('default', 'register', 'failure', 'join_form')
    


