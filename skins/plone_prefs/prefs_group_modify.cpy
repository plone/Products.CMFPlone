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
    groupstool.editGroup(group, roles=roles, groups=(), REQUEST=context.REQUEST)
    message = _(u'Changes saved.')

delete=REQUEST.get('delete',[])

if delete:
    groupstool.removeGroups(delete, REQUEST=context.REQUEST)
    message=_(u'Group(s) deleted.')

context.plone_utils.addPortalMessage(message)
return state
