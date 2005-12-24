## Script (Python) "folder_localrole_set"
##parameters=use_acquisition=0, use_portraits=0
##title=set acquitision
##

putils = context.plone_utils
putils.acquireLocalRoles(context, use_acquisition)
if use_acquisition:
    msg1="Role Acquisition is now turned on, "
else:
    msg1="Role Acquisition is now turned off, "

if use_portraits:
    msg2="Portraits turned on"
else:
    msg2="Portraits turned off"

# set the portrait cookie
context.REQUEST.RESPONSE.setCookie('usePortraits',use_portraits,path="/")

qst='?portal_status_message=%s%s.' %(msg1,msg2)

from Products.CMFPlone.utils import transaction_note
transaction_note('Modified acquisition settings for folder %s at %s' % (context.title_or_id(), context.absolute_url()))

context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/folder_localrole_form' + qst )
