## Script (Python) "logout"
##title=Logout handler
##parameters=
REQUEST = context.REQUEST
if REQUEST.has_key('portal_skin'):
   context.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
REQUEST.SESSION.invalidate()
return REQUEST.RESPONSE.redirect(REQUEST.URL1+'/logged_out')
