## Script (Python) "folder_localrole_edit"
##parameters=change_type, member_ids=(), member_role=[]
##title=Set local roles
##

from Products.CMFPlone import transaction_note
from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus

pm = context.portal_membership

if change_type == 'add':
    # Keep backward-compatibility
    if same_type(member_role, ''):
        member_role = [member_role]
    for role in member_role:
        pm.setLocalRoles( obj=context,
                          member_ids=member_ids,
                          member_role=role )
else:
    pm.deleteLocalRoles( obj=context,
                         member_ids=member_ids )

msg=_(u'Local roles changed.')

transaction_note('Modified sharing for folder %s at %s' % (context.title_or_id(), context.absolute_url()))

context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_localrole_form?portal_status_message=' + url_quote_plus(msg))
