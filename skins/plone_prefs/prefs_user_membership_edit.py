## Script (Python) "prefs_group_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid
##title=Edit user's group membership
##
REQUEST=context.REQUEST

delete = REQUEST.get('delete', [])
for groupname in delete:
    group = context.portal_groups.getGroupById(groupname)
    group.removeMember(userid)

add = REQUEST.get('add', [])
for groupname in add:
    group = context.portal_groups.getGroupById(groupname)
    group.addMember(userid)

return container.prefs_user_memberships()
