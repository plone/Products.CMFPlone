## Script (Python) "folder_localrole_edit"
##parameters=change_type, member_ids=(), member_role=[]
##title=Set local roles
##

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

pm = context.portal_membership

if change_type == 'add':
    # Keep backward-compatibility
    if same_type(member_role, ''):
        member_role = [member_role]
    for role in member_role:
        pm.setLocalRoles( obj=context,
                          member_ids=member_ids,
                          member_role=role,
                          REQUEST=context.REQUEST)
else:
    pm.deleteLocalRoles( obj=context,
                         member_ids=member_ids,
			 REQUEST=context.REQUEST )

transaction_note('Modified sharing for folder %s at %s' % (context.title_or_id(), context.absolute_url()))
context.plone_utils.addPortalMessage(_(u'Local roles changed.'))

context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_localrole_form')
