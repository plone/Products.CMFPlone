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

isAnonymous = membership_tool.isAnonymousUser()

# If you log in with cookies disabled, you will appear to be logged
# in when you hit login.py.  To make sure you are really logged in,
# we force the page to reload and then test for login status.
#
# Look for the REQUEST variable 'success' -- if it's not present,
# redirect to the current page.
# 
# Commented out the code below because it broke older IE's and
# most importantly Safari
"""
success = REQUEST.get('success',None)
if success is None:
    # 'success' variable not found -- create it and reload the page
    args = REQUEST.form
    args['success'] = int(not isAnonymous)
    url = '%s?%s' % (REQUEST.URL, ZTUtils.make_query(args))
    # make sure the redirect header we are about to send isn't cached!
    REQUEST.RESPONSE.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
    REQUEST.RESPONSE.setHeader('Pragma', 'no-cache')
    return REQUEST.RESPONSE.redirect(url)
"""

login_failed = 'login_failed'
login_changepassword = 'login_password'

login_success = REQUEST.get('came_from', REQUEST.get('HTTP_REFERER'))

# if we weren't called from something that set 'came_from' and we don't
# have an HTTP_REFERER (extremely unlikely), or if either came_from or
# HTTP_REFERER were the 'logged_out' page, return the default 'login_success'
# form
if login_success is None or login_success.endswith('logged_out'):
    login_success = '%s/%s' % (context.portal_url(), 'login_success')

if isAnonymous:
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    return context.restrictedTraverse(login_failed)()

member = membership_tool.getAuthenticatedMember()

if  ( str(member.getProperty('login_time', None)) == '2000/01/01' and
      context.validate_email ):
    return context.restrictedTraverse(login_changepassword)()

# this will create the memberarea if necessary, but the called code
# doesn't blow up if the memberarea already exists
membership_tool.createMemberArea()

qs = context.create_query_string(REQUEST.get('QUERY_STRING', ''),
                                 portal_status_message="You're logged in now")
return REQUEST.RESPONSE.redirect('%s?%s' % (login_success, qs))


