## Controller Python Script "prefs_group_members_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=groupname, delete=[]
##title=Edit group members
##

from Products.CMFPlone import PloneMessageFactory as _

REQUEST=context.REQUEST
group=context.portal_groups.getGroupById(groupname)

for u in delete:
    group.removeMember(u, REQUEST=context.REQUEST)

context.plone_utils.addPortalMessage(_(u'Changes saved.'))
return state
