## Script (Python) "prefs_user_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid
##title=Edit user
##
REQUEST=context.REQUEST
member=context.portal_membership.getMemberById(userid)

context.plone_utils.setMemberProperties(member, **REQUEST.form)

print REQUEST
return printed

REFERER=REQUEST.HTTP_REFERER
statusmsg=REFERER.find('portal_status_message')
url='%s&%s' % (REFERER[:REFERER.find('portal_status_message')],
               'portal_status_message=Changes+made.')
return REQUEST.RESPONSE.redirect(url)
