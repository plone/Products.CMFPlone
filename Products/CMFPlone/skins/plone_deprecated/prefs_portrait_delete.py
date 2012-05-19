## Script (Python) "prefs_portrait_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid, portrait=''
##title=Edit user

from Products.CMFPlone import PloneMessageFactory as _

#update portrait
REQUEST = context.REQUEST
portal_membership = context.portal_membership
member = portal_membership.getMemberById(userid)

portal_membership.deletePersonalPortrait(userid)
context.plone_utils.addPortalMessage(_(u'Portrait deleted.'))

return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
