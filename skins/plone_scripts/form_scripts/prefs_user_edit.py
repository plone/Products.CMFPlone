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

processed={}
for id, property in context.portal_memberdata.propertyItems():
    processed[id]=REQUEST.get(id, None)
    
context.plone_utils.setMemberProperties(member, **processed)

REFERER=REQUEST.HTTP_REFERER
if REFERER.find('portal_status_message')!=-1:
    REFERER=REFERER[:REFERER.find('portal_status_message')]
url='%s&%s' % (REFERER, 'portal_status_message=Changes+made.')
return REQUEST.RESPONSE.redirect(url)
