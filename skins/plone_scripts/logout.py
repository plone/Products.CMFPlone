## Script (Python) "logout"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Logout handler
##parameters=
REQUEST = context.REQUEST
if REQUEST.has_key('portal_skin'):
   context.portal_skins.clearSkinCookie()
cookie_name=context.cookie_authentication.getProperty('auth_cookie')
REQUEST.RESPONSE.expireCookie(cookie_name, path='/')
REQUEST.SESSION.invalidate()
return REQUEST.RESPONSE.redirect(REQUEST.URL1+'/logged_out')
