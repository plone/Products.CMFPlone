## Script (Python) "prefs_group_members_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=groupname
##title=Edit group members
##
REQUEST=context.REQUEST
group=context.portal_groups.getGroupById(groupname)

delete = REQUEST.get('delete', [])
for u in delete:
    group.removeMember(u)

add = REQUEST.get('add',[])
for u in add:
   group.addMember(u)

return container.prefs_group_members()
