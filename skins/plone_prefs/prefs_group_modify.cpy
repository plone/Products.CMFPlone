## Script (Python) "prefs_group_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Modify groups
##

from Products.CMFPlone import PloneMessageFactory as _

REQUEST=context.REQUEST
groupstool=context.portal_groups
message = _(u'No changes done.')

groups=[group[len('group_'):]
        for group in REQUEST.keys()
        if group.startswith('group_')]

for group in groups:
    roles=[r for r in REQUEST['group_' + group] if r]
    groupstool.editGroup(group, roles=roles, groups=())
    message = _(u'Changes saved.')

delete=REQUEST.get('delete',[])

if delete:
    groupstool.removeGroups(delete)

    if (1 < len(delete)):
        message=_(u'Groups ${names} have been deleted.')
        message.mapping[u'names'] = ', '.join(delete)
    else:
        message=_(u'Group ${name} has been deleted.')
        message.mapping[u'name'] = ''.join(delete)

return state.set(portal_status_message=message)
