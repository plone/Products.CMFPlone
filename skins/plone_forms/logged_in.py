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
# in when you hit login.py.  To see if a login failure is due to 
# cookies being disabled, we test a session cookie that is set by main_template.  
# This isn't foolproof, but it should catch most cases.
# *********************************************************************
# To enable this testing, you need to set the variable test_cookie in *
# site_properties to a non-empty value.                               *
# *********************************************************************
#

no_cookies = 0
test_cookie_name = getattr(properties_tool, 'test_cookie_name', None)
if test_cookie_name:
    test_cookie = REQUEST.cookies.get(test_cookie_name, None)
    if test_cookie is None:
        no_cookies = 1
        
login_failed = 'login_failed'
login_changepassword = 'login_password'
login_success = 'login_success'
pagetemplate=None

if isAnonymous or no_cookies:
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    REQUEST.set('no_cookies', no_cookies)
    return context.restrictedTraverse(login_failed)()

member = membership_tool.getAuthenticatedMember()

if member.getProperty('login_time', None) == '2000/01/01' and properties_tool.validate_email:
    return context.restrictedTraverse(login_changepassword)()

return context.restrictedTraverse(login_success)()