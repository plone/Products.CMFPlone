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
tool = context.portal_groups

for u in delete:
    tool.removePrincipalFromGroup(u, groupname, REQUEST)

context.plone_utils.addPortalMessage(_(u'Changes saved.'))
return state
