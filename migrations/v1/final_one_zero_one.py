from Products.CMFPlone import MigrationTool
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

def onezeroone(portal):
    """ Upgrade from Plone 1.0 to Plone 1.0.1"""

    # Setup navigation for syndication
    nav_props = portal.portal_properties.navigation_properties
    nav = (('default.synPropertiesForm.success', 'script:editSynProperties'),
           ('default.synPropertiesForm.failure', 'synPropertiesForm'),
           ('default.editSynProperties.success', 'url:folder_contents'),
           ('default.editSynProperties.failure', 'synPropertiesForm')
           )

    for id, action in nav:
        if nav_props.hasProperty(id):
            nav_props._updateProperty(id, action)
        else:
            nav_props._setProperty(id, action)

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


def registerMigrations():
    MigrationTool.registerUpgradePath(
            '1.0',
            '1.0.1',
            onezeroone
            )

if __name__=='__main__':
    registerMigrations()
