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

from Products.CMFPlone import PloneMessageFactory as _

REQUEST=context.REQUEST
tool = context.portal_groups

for u in add:
    tool.addPrincipalToGroup(u, groupname, REQUEST)

context.plone_utils.addPortalMessage(_(u'Changes made.'))
return state