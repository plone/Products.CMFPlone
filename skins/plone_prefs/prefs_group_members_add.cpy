## Controller Python Script "prefs_group_members_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=groupname, add=[]
##title=Edit group members
##

REQUEST=context.REQUEST
group=context.portal_groups.getGroupById(groupname)

for u in add:
    group.addMember(u)

return state.set(portal_status_message = 'Changes made.')
