## Controller Python Script "logged_in"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Initial post-login actions

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

REQUEST = context.REQUEST

membership_tool = getToolByName(context, 'portal_membership')
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    email_login = context.portal_registry['plone.use_email_as_login']
    if email_login:
        context.plone_utils.addPortalMessage(
            _(u'Login failed. Both email address and password are case '
              u'sensitive, check that caps lock is not enabled.'),
            'error')
    else:
        context.plone_utils.addPortalMessage(
            _(u'Login failed. Both login name and password are case '
              u'sensitive, check that caps lock is not enabled.'),
            'error')
    return state.set(status='failure')

from DateTime import DateTime
member = membership_tool.getAuthenticatedMember()
login_time = member.getProperty('login_time', '2000/01/01')
if not isinstance(login_time, DateTime):
    login_time = DateTime(login_time)
initial_login = int(login_time == DateTime('2000/01/01'))
state.set(initial_login=initial_login)

must_change_password = member.getProperty('must_change_password', 0)
state.set(must_change_password=must_change_password)

if initial_login:
    state.set(status='initial_login')
elif must_change_password:
    state.set(status='change_password')

membership_tool.loginUser(REQUEST)

return state
