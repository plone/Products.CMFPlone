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

delete = REQUEST.get('delete', [])

for groupname in delete:
    group = context.portal_groups.getGroupById(groupname)
    group.removeMember(userid)

REFERER=REQUEST.HTTP_REFERER
if REFERER.find('portal_status_message')!=-1:
    REFERER=REFERER[:REFERER.find('portal_status_message')]
url='%s&%s' % (REFERER, 'portal_status_message= ' + `delete` + ' removed')
return REQUEST.RESPONSE.redirect(url)
