## Controller Python Script "reconfig"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure Portal
state = context.portal_form_controller.getState(script, is_validator=0)

REQUEST=context.REQUEST
portal_properties=context.portal_properties
portal_properties.editProperties(REQUEST)
portal_properties.site_properties.manage_changeProperties(REQUEST)
context.portal_url.getPortalObject().manage_changeProperties(REQUEST)

default_skin=context.portal_skins.getDefaultSkin()
context.plone_utils.setDefaultSkin(REQUEST.get('default_skin', default_skin))

return state.set(portal_status_message='Portal reconfigured.')
