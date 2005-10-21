## Script (Python) "folder_localrole_set"
##parameters=use_acquisition=0, use_portraits=0
##title=set acquitision
##

from Products.CMFPlone import transaction_note
from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus

putils = context.plone_utils
putils.acquireLocalRoles(context, use_acquisition)
if use_acquisition:
    msg1=_(u'Role Acquisition is now turned on.')
else:
    msg1=_(u'Role Acquisition is now turned off.')

if use_portraits:
    msg2=_(u'Portraits turned on.')
else:
    msg2=_(u'Portraits turned off.')

# set the portrait cookie
context.REQUEST.RESPONSE.setCookie('usePortraits',use_portraits,path="/")

msg='%s+%s.' % (url_quote_plus(msg1), url_quote_plus(msg2))

transaction_note('Modified acquisition settings for folder %s at %s' % (context.title_or_id(), context.absolute_url()))

context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_localrole_form?portal_status_message=' + msg)

