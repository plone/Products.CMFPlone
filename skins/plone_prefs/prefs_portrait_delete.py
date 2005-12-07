## Script (Python) "prefs_portrait_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid, portrait=''
##title=Edit user
##

from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus

#update portrait
REQUEST=context.REQUEST
portal_membership = context.portal_membership
member=portal_membership.getMemberById(userid)

portal_membership.deletePersonalPortrait(userid)

REFERER=REQUEST.HTTP_REFERER
if REFERER.find('portal_status_message')!=-1:
    REFERER=REFERER[:REFERER.find('portal_status_message')]

msg = _(u'Portrait deleted.')

url='%s&portal_status_message=%s' % (REFERER, url_quote_plus(msg))
return REQUEST.RESPONSE.redirect(url)
