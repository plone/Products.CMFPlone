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

mt=context.portal_membership
if mt.isAnonymousUser():
    # not logged in -- most likely because cookies not enabled
    state.set(status='failure_anonymous', portal_status_message='You must enable cookies before you can log in.')
    return state

request = context.REQUEST
password = request.get('password', None)
password_confirm = request.get('confirm', None)

failMessage=context.portal_registration.testPasswordValidity(password, password_confirm)
if failMessage:
    state.setError('password', failMessage)
    state.set(status='failure', portal_status_message=failMessage)
    return state

if password != password_confirm:
    state.setError('confirm', 'Passwords must match')
    state.set(status='failure', portal_status_message='Please make sure you confirm your password.')
    return state

return state