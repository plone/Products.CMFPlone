## Script (Python) "logout"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Logout handler
##parameters=

REQUEST = context.REQUEST
# if REQUEST.has_key('portal_skin'):
#   context.portal_skins.clearSkinCookie()

skinvar = context.portal_skins.getRequestVarname()
path = '/' + context.absolute_url(1)

if REQUEST.has_key(skinvar) and not context.portal_skins.getCookiePersistence():
    REQUEST.RESPONSE.expireCookie(skinvar, path=path)

cookie_name=context.cookie_authentication.getProperty('auth_cookie')
REQUEST.RESPONSE.expireCookie(cookie_name, path='/')
REQUEST.SESSION.invalidate()
from Products.CMFPlone import transaction_note
transaction_note('Logged out')
return state.set(next_action='redirect_to:string:'+REQUEST.URL1+'/logged_out')
