from migration_util import safeEditProperty

from Products.CMFPlone import MigrationTool
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

def onezeroone(portal):
    """ Upgrade from Plone 1.0 to Plone 1.0.1"""
    # Setup utf-8 encoding
    sp = portal.portal_properties.site_properties
    k = 'default_charset'
    v = 'utf-8'
    safeEditProperty(sp, k, v)

    # Setup navigation for syndication
    nav_props = portal.portal_properties.navigation_properties
    nav = (('default.synPropertiesForm.success', 'script:editSynProperties'),
           ('default.synPropertiesForm.failure', 'synPropertiesForm'),
           ('default.editSynProperties.success', 'url:folder_contents'),
           ('default.editSynProperties.failure', 'synPropertiesForm')
           )
    
    for id, action in nav:
        safeEditProperty(nav_props, id, action)

    # Add validation of syndication form
    form_tool = portal.portal_form
    form_tool.setValidators('synPropertiesForm', ['validate_synPropertiesForm'])

    # Change syndication action to use portal_form
    #make 'syndication' tab unvisible
    st=getToolByName(portal, 'portal_syndication')
    st_actions=st._cloneActions()
    for a in st_actions:
        if a.id=='syndication':
            a.action=Expression('string:${folder_url}/portal_form/synPropertiesForm')
    st._actions=st_actions
