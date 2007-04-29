## Script (Python) "folder_localrole_delete"
##parameters=member_ids=(), member_role_ids=[]
##title=Delete local roles
##

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

pm = context.portal_membership
pu = context.plone_utils

reindex=False
# first look for members
if len(member_ids)>0:
    reindex=True
    pm.deleteLocalRoles( obj=context,
                         member_ids=member_ids,
			 reindex=False,
			 REQUEST=context.REQUEST)

def parseMemberRoleString( s ):
    sidx = s.find('((')
    eidx = s.find('))')
    if sidx == -1 or eidx == -1:
        return None
    return s[:sidx], s[sidx+2:eidx]

#
# second look for certain roles
#
if len(member_role_ids)>0:
    reindex=True

    # get all local roles 
    local_roles=context.acl_users.getLocalRolesForDisplay(context)

    # sort members first
    members={}
    for s in member_role_ids:
        member_role = parseMemberRoleString(s)
        if member_role is None: 
            continue
        member,role=member_role
        members.setdefault(member,[]).append(role)

    # now process the dictionary of the form {member: roles to delete}
    for member_id, roles_to_delete in members.items():
        # filter the actual member roles from the local roles
        roles_for_member=[]
        for role in local_roles:
            if role[3]==member_id:
                roles_for_member.extend(list(role[1]))

        newRoles=[r for r in roles_for_member if r not in roles_to_delete] 

        # delete all roles for that member
        pm.deleteLocalRoles( obj=context,
                             member_ids=(member_id,),
			     reindex=False,
			     REQUEST=context.REQUEST)

        # add the other roles again
        for role in newRoles:
            pm.setLocalRoles( obj=context,
                          member_ids=(member_id,),
                          member_role=role,
			  reindex=False)

if reindex:
    context.reindexObjectSecurity()

transaction_note('Modified sharing for folder %s at %s' % (context.title_or_id(), context.absolute_url()))
context.plone_utils.addPortalMessage(_(u'Local roles deleted.'))

context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_localrole_form')
