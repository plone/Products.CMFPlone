## Script (Python) "validate_login_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validate password change during login
##

from Products.CMFPlone import PloneMessageFactory as _

mt=context.portal_membership
if mt.isAnonymousUser():
    # not logged in -- most likely because cookies not enabled
    context.plone_utils.addPortalMessage(_(u'You must enable cookies before you can log in.'), 'error')
    state.set(status='failure_anonymous')
    return state

request = context.REQUEST
password = request.get('password', None)
password_confirm = request.get('confirm', None)

failMessage=context.portal_registration.testPasswordValidity(password, password_confirm)
if failMessage:
    context.plone_utils.addPortalMessage(failMessage, 'error')
    state.setError('password', failMessage)
    state.set(status='failure')
    return state

if password != password_confirm:
    context.plone_utils.addPortalMessage(_(u'Please make sure you confirm your password.'), 'error')
    state.setError('confirm', _(u'Passwords must match.'))
    state.set(status='failure')
    return state

return state
