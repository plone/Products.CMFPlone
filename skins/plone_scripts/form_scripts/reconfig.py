# Script (Python) "reconfig"
##title=Reconfigure Portal
##parameters=
REQUEST=context.REQUEST
context.portal_properties.editProperties(REQUEST)
default_skin=context.portal_skins.getDefaultSkin()
context.plone_utils.setDefaultSkin(REQUEST.get('default_skin', default_skin))
return ('success', context)
