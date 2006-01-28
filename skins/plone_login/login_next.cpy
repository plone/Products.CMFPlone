## Controller Python Script "login_next"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Login next actions
##
from DateTime import DateTime
import ZTUtils

REQUEST = context.REQUEST

membership_tool = context.portal_membership
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    return state.set(status='failure', portal_status_message='Login failed')

came_from = REQUEST.get('came_from', None)
util = context.plone_utils

# if we weren't called from something that set 'came_from' or if HTTP_REFERER
# is the 'logged_out' page, return the default 'login_success' form
if came_from is not None:
    scheme, location, path, parameters, query, fragment = util.urlparse(came_from)
    template_id = path.split('/')[-1]
    if template_id in ['login', 'login_success', 'login_password', 'login_failed',
                       'login_form', 'logged_in', 'logged_out', 'registered',
                       'mail_password', 'mail_password_form', 'join_form',
                       'require_login', 'member_search_results']:
        came_from = ''
    # It is probably a good idea in general to filter out urls outside the portal.
    # An added bonus: this fixes some problems with a Zope bug that doesn't
    # properly unmangle the VirtualHostMonster stuff when setting ACTUAL_URL
    if not context.portal_url.isURLInPortal(came_from):
        came_from = ''

js_enabled = REQUEST.get('js_enabled','1') != '0'
if came_from and js_enabled:
    # If javascript is not enabled, it is possible that cookies are not enabled.
    # If cookies aren't enabled, the redirect will log the user out, and confusion
    # may arise.  Redirect only if we know for sure that cookies are enabled.

    # Add portal_status_message to the query string of the url we came from
    query = context.create_query_string(query, portal_status_message='Welcome! You are now logged in.')
    came_from = util.urlunparse((scheme, location, path, parameters, query, fragment))
    REQUEST.RESPONSE.redirect(came_from)

state.set(came_from=came_from)

return state
