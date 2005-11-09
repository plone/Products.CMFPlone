## Script (Python) "logout"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Logout handler
##parameters=

from Products.CMFCore.utils import getToolByName

REQUEST = context.REQUEST

skinvar = context.portal_skins.getRequestVarname()
path = '/' + context.absolute_url(1)

if (REQUEST.has_key(skinvar) and
    not context.portal_skins.getCookiePersistence()):
    REQUEST.RESPONSE.expireCookie(skinvar, path=path)

cookie_auth = getToolByName(context, 'cookie_authentication', None)
if cookie_auth is not None:
    cookie_name = cookie_auth.getProperty('auth_cookie')
    REQUEST.RESPONSE.expireCookie(cookie_name, path='/')

# Invalidate existing sessions, but only if they exist.
sdm = getToolByName(context, 'session_data_manager', None)
if sdm is not None:
    session = sdm.getSessionData(create=0)
    if session is not None:
        session.invalidate()

from Products.CMFPlone import transaction_note
transaction_note('Logged out')

target_url = REQUEST.URL1
# Double '$' to avoid injection into TALES
target_url = target_url.replace('$','$$')
target_url += '/logged_out'
return state.set(next_action='redirect_to:string:' + target_url )
