## Script (Python) "prefs_portal_properties_set"
## Giuseppe Masili <giuseppe@linux.it> 2003
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=prefs_portal_properties_set
##

REQUEST=context.REQUEST
attr = REQUEST.get('attr','')
mh = getattr(context.portal_properties, attr)
mh.manage_editProperties(REQUEST.form)
msg = 'Updated.'
REQUEST.RESPONSE.redirect('prefs_portal_properties?attr=' + attr + '&portal_status_message=' + msg)
return 0
