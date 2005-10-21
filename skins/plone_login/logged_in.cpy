## Script (Python) "logged_in"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Initial post-login actions
##

from Products.CMFPlone import PloneMessageFactory as _
REQUEST=context.REQUEST

# If someone has something on their clipboard, expire it.
if REQUEST.get('__cp', None) is not None:
    REQUEST.RESPONSE.expireCookie('__cp', path='/')

membership_tool=context.portal_membership
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    return state.set(status='failure', portal_status_message=_(u'Login failed'))

member = membership_tool.getAuthenticatedMember()
login_time = member.getProperty('login_time', '2000/01/01')
if  str(login_time) == '2000/01/01':
    state.set(status='initial_login', initial_login=True)

membership_tool.setLoginTimes()
membership_tool.createMemberArea()

return state
