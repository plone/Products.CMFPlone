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

cookie_auth=getattr(context, 'cookie_authentication')
if cookie_auth is not None:
    cookie_name=cookie_auth.getProperty('auth_cookie')
    REQUEST.RESPONSE.expireCookie(cookie_name, path='/')

# This sort of sucks.  If you do not have SESSIONS enabled
# this throws an exception ;-(.  You can not try/except
# around calling invalidate.  It will throw excpetion
# regardless.  No idea how chrism managed that one *wink*
REQUEST.SESSION.invalidate()
from Products.CMFPlone import transaction_note
transaction_note('Logged out')

# If you want to do a traverse next, instead of a redirect, you need to
# kill the current security context.  Keep in mind that this may mean
# that you end up on a logged_out page with a context that you can't view...
# context.portal_membership.immediateLogout()

return state.set(next_action='redirect_to:string:'+REQUEST.URL1+'/logged_out')
