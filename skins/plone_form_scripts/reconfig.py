## Script (Python) "reconfig"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure Portal

REQUEST=context.REQUEST
portal_properties=context.portal_properties
portal_properties.editProperties(REQUEST)
portal_properties.site_properties.manage_changeProperties(REQUEST)
context.portal_url.getPortalObject().manage_changeProperties(REQUEST)

default_skin=context.portal_skins.getDefaultSkin()
context.plone_utils.setDefaultSkin(REQUEST.get('default_skin', default_skin))
return ( 'success'
       , context
       , {'portal_status_message' : REQUEST.get( 'portal_status_message'
                                               , 'Portal reconfigured.')} )
