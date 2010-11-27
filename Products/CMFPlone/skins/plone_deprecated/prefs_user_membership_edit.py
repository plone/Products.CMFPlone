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
RESPONSE=REQUEST.RESPONSE

gtool = context.portal_groups

delete = REQUEST.get('delete', [])
for groupname in delete:
    gtool.removePrincipalFromGroup(userid, groupname, REQUEST)

add = REQUEST.get('add', [])
for groupname in add:
    gtool.addPrincipalToGroup(userid, groupname, REQUEST)

return RESPONSE.redirect('%s?userid=%s' % (container.prefs_user_memberships.absolute_url(),
                                           userid)
                        )
