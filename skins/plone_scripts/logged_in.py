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
properties_tool=context.portal_properties.site_properties
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
login_success = 'login_success'
pagetemplate=None

if isAnonymous:
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    return context.restrictedTraverse(login_failed)()

member = membership_tool.getAuthenticatedMember()

if member.getProperty('login_time', None) == '2000/01/01' and properties_tool.validate_email:
    return context.restrictedTraverse(login_changepassword)()

return context.restrictedTraverse(login_success)()
