## Script (Python) "prefs_group_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Modify groups
##
REQUEST=context.REQUEST
groupstool=context.portal_groups
message = 'No changes done.'

groups=[group[len('group_'):]
        for group in REQUEST.keys()
        if group.startswith('group_')]

for group in groups:
    roles=[r for r in REQUEST['group_' + group] if r]
    groupstool.editGroup(group, roles=roles, groups=())
    message = 'Changes saved.'

delete=REQUEST.get('delete',[])

if delete:
    groupstool.removeGroups(delete)

    if (1 < len(delete)):
        message=context.translate(
            "Groups ${names} have been deleted.",
            {'names': ', '.join(delete)})
    else:
        message=context.translate(
            "Group ${name} has been deleted.",
            {'name': ''.join(delete)})

context.plone_utils.addPortalMessage(message)
return state
