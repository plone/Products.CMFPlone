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
REQUEST=context.REQUEST
properties_tool=context.portal_properties.site_properties
membership_tool=context.portal_membership

isAnonymous = membership_tool.isAnonymousUser()
login_failed = 'login_failed'
login_changepassword = 'login_password'
login_success = 'login_success'
pagetemplate=None

member = membership_tool.getAuthenticatedMember()

if isAnonymous:
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    pagetemplate=context.restrictedTraverse(login_failed)

if pagetemplate is None and member.getProperty('login_time', None) == '2000/01/01' and \
  properties_tool.validate_email:
    pagetemplate=context.restrictedTraverse(login_changepassword)

if pagetemplate is None and not(member.getProperty('login_time', None) == '2000/01/01' and properties_tool.validate_email):
    pagetemplate=context.restrictedTraverse(login_success)

return pagetemplate()
