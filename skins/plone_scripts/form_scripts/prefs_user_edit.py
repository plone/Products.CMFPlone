## Script (Python) "prefs_user_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id
##title=Edit user
##
REQUEST=context.REQUEST
membership=context.portal_membership
setMemberProperties=context.plone_utils
member=membership.getMemberById(id)

print REQUEST
return printed


REFERER=REQUEST.HTTP_REFERER
statusmsg=REFERER.find('portal_status_message')
url='%s&%s' % (REFERER[:REFERER.find('portal_status_message')],
               'portal_status_message=Changes+made.')
return REQUEST.RESPONSE.redirect(url)
