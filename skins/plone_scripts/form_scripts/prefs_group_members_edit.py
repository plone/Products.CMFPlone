## Script (Python) "prefs_group_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=groupname
##title=Edit group members
##
REQUEST=context.REQUEST
group=context.portal_groups.getGroupById(groupname)

delete = REQUEST.get('delete', [])

for u in delete:
    group.removeMember(u)

REFERER=REQUEST.HTTP_REFERER
if REFERER.find('portal_status_message')!=-1:
    REFERER=REFERER[:REFERER.find('portal_status_message')]
url='%s&%s' % (REFERER, 'portal_status_message= ' + `delete` + ' removed')
return REQUEST.RESPONSE.redirect(url)
