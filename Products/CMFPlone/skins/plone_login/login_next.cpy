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

from Products.CMFPlone import PloneMessageFactory as _
from DateTime import DateTime
import ZTUtils

REQUEST = context.REQUEST

util = context.plone_utils
membership_tool=context.portal_membership
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    util.addPortalMessage(_(u'Login failed'), 'error')
    return state.set(status='failure')

came_from = REQUEST.get('came_from', None)
next = REQUEST.get('next', None)

# if we weren't called from something that set 'came_from' or if HTTP_REFERER
# is the 'logged_out' page, return the default 'login_success' form
if came_from is not None:
    scheme, location, path, parameters, query, fragment = util.urlparse(came_from)
    template_id = path.split('/')[-1]
    if template_id in ['login', 'login_success', 'login_password', 'login_failed',
                       'login_form', 'logged_in', 'logout', 'logged_out', 'registered',
                       'mail_password', 'mail_password_form', 'register',
                       'require_login', 'member_search_results', 'pwreset_finish',
                       # We need localhost in the list, or Testing.testbrowser
                       # tests won't be able to log in via login_form
                       'localhost']:
        came_from = ''
    # It is probably a good idea in general to filter out urls outside the portal.
    # An added bonus: this fixes some problems with a Zope bug that doesn't
    # properly unmangle the VirtualHostMonster stuff when setting ACTUAL_URL
    if not context.portal_url.isURLInPortal(came_from):
        came_from = ''

if next:
    if not context.portal_url.isURLInPortal(next):
        came_from = next = ''
    else:
        state.set(status='external')

if came_from and not next:
    # If javascript is not enabled, it is possible that cookies are not enabled.
    # If cookies aren't enabled, the redirect will log the user out, and confusion
    # may arise.  Redirect only if we know for sure that cookies are enabled.

    util.addPortalMessage(_(u'Welcome! You are now logged in.'))
    came_from = util.urlunparse((scheme, location, path, parameters, query, fragment))

    # redirect immediately
    return REQUEST.RESPONSE.redirect(came_from)

state.set(came_from=came_from, next=next)

return state
