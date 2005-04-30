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
util = context.plone_utils

isAnonymous = membership_tool.isAnonymousUser()

login_failed = 'login_failed'
login_changepassword = 'login_password'
login_success = None
came_from = REQUEST.get('came_from')

# If someone has something on their clipboard, expire it.
if REQUEST.get('__cp', None) is not None:
    REQUEST.RESPONSE.expireCookie('__cp', path='/')

# if we weren't called from something that set 'came_from' or if HTTP_REFERER
# is the 'logged_out' page, return the default 'login_success' form
if came_from is not None:
    template_id = came_from.split('?')[0].split('/')[-1]
if not came_from or \
   template_id.endswith('logged_out') or \
   template_id.endswith('mail_password') or \
   template_id.endswith('member_search_results') or \
   template_id.endswith('login_form'):
    login_success = '%s/%s' % (context.portal_url(), 'login_success')

if isAnonymous:
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    return context.restrictedTraverse(login_failed)()

member = membership_tool.getAuthenticatedMember()

login_time = member.getProperty('login_time', context.ZopeTime())
member.setProperties(last_login_time = login_time,
                     login_time = context.ZopeTime())

if  ( str(login_time) == '2000/01/01' and
      context.validate_email ):
    return context.restrictedTraverse(login_changepassword)()


if hasattr(membership_tool, 'createMemberArea'):

    # This is acutally a capablities test.  For non-mgmt users, the
    # hasattr test above test will fail under CMF 1.4 but will succeed
    # under CMF HEAD due do security machinery magic.  Hasattr will
    # return false under CMF 1.4 because the createMemberArea method
    # is protected by 'Manage portal' permission.  Under CMF HEAD+,
    # createMemberArea is declared public, so it will succeed.

    # This is necessary because in CMF 1.4, the wrapUser method
    # creates a member folder automatically.  However under the HEAD,
    # it is this script's responsibility to do so.  So we only want to
    # call createMemberArea under CMF HEAD+.

    membership_tool.createMemberArea()


# Add portal_status_message to the query string of the we came from

if login_success:
    dest=login_success
else:
    # set the standard location to return
    REFERER = REQUEST.get('HTTP_REFERER', login_success)
    scheme, location, path, parameters, query, fragment = util.urlparse(REFERER)

    # allow over-rides by request params
    came_from=REQUEST.get('came_from', None)
    if came_from:
        scheme, location, path, parameters, x, fragment = util.urlparse(came_from)
    query = REQUEST.get('came_from_query', query)

    query = context.create_query_string(query, portal_status_message=("Welcome! You are now logged in."))

    # put everything back together
    dest = util.urlunparse((scheme, location, path, parameters, query, fragment))

return REQUEST.RESPONSE.redirect(dest)