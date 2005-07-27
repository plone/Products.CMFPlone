## Script (Python) "logged_in"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=login
##
from DateTime import DateTime
import ZTUtils

REQUEST=context.REQUEST

membership_tool=context.portal_membership
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    return state.set(status='failure', portal_status_message='Login failed')

came_from = REQUEST.get('came_from', None)
# if we weren't called from something that set 'came_from' or if HTTP_REFERER
# is the 'logged_out' page, return the default 'login_success' form
if came_from is not None:
    template_id = came_from.split('?')[0].split('/')[-1]
    if template_id in ['login', 'login_success', 'login_password', 'login_failed', 'login_form', 'logged_in', 'logged_out', 'registered', 'mail_password', 'mail_password_form', 'join_form', 'require_login', 'member_search_results']:
        came_from = ''

#if came_from:
#    util = context.plone_utils
#    # Add portal_status_message to the query string of the url we came from
#    scheme, location, path, parameters, query, fragment = util.urlparse(came_from)
#    query = context.create_query_string(query, portal_status_message='Welcome! You are now logged in.')
#    came_from = util.urlunparse(scheme, location, path, parameters, query, fragment)

state.set(came_from=came_from)
return state
