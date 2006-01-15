## Script (Python) "folder_localrole_add"
##parameters=member_ids=(), member_roles=()
##title=Set local roles
##
pm = context.portal_membership

for member_role in member_roles:
    pm.setLocalRoles( obj=context,
                      member_ids=member_ids,
                      member_role=member_role )

qst='?portal_status_message=Local+Roles+changed.'

from Products.CMFPlone.utils import transaction_note
transaction_note('Modified sharing for folder %s at %s' % (context.title_or_id(), context.absolute_url()))

context.REQUEST.RESPONSE.redirect( context.absolute_url() + '/folder_localrole_form' + qst )
