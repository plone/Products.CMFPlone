## Script (Python) "prefs_group_manage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Manage groups
##
REQUEST=context.REQUEST
groupstool=context.portal_groups
portal_status_message = 'No changes done.'

groups=[group[len('group_'):]
        for group in REQUEST.keys()
        if group.startswith('group_')]

for group in groups:
    roles=REQUEST['group_' + group]
    groupstool.editGroup(group, roles=roles, groups=())
    portal_status_message = 'Changes saved.'

delete=REQUEST.get('delete',[])

if delete:
    groupstool.removeGroups(delete)

    if (1 < len(delete)):
        portal_status_message=context.translate(
            "Groups ${names} have been deleted.",
            {'names': ', '.join(delete)})
    else:
        portal_status_message=context.translate(
            "Group ${name} has been deleted.",
            {'name': ''.join(delete)})

return state.set(portal_status_message=portal_status_message)
