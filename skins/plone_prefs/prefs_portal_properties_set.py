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

from Products.CMFPlone import PloneMessageFactory as _

REQUEST=context.REQUEST
attr = REQUEST.get('attr','')
mh = getattr(context.portal_properties, attr)
mh.manage_editProperties(REQUEST.form)
context.plone_utils.addPortalMessage(_(u'Updated.'))

REQUEST.RESPONSE.redirect('prefs_portal_properties?attr=' + attr)
return 0
