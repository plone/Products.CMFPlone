## Controller Python Script "validate_registration"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates the Registration of a User

REQUEST=context.REQUEST

validator = context.portal_form.createForm()
validator.addField('username', 'String', required=1)
validator.addField('email', 'Email')
properties = context.portal_properties.site_properties
if not properties.validate_email:
    # if we are validating email we aren't letting people pick their own passwords.
    validator.addField('password', 'Password', required=1)
    validator.addField('confirm', 'Password', required=1)
errors = validator.validate(REQUEST)
for fieldid, error in errors.items():
    state.setError(fieldid, error)

password, confirm = REQUEST.get('password', ''), REQUEST.get('confirm', '')

#manual validation ;(
if not properties.validate_email:
    if password!=confirm:
        state.setError('password', 'Passwords do not match.')
        state.setError('confirm', 'Passwords do not match.')
    if not state.getError('password') and len(password) < 5:
        state.setError('password', 'Passwords must contain at least 5 letters.')
        state.setError('confirm', 'Passwords must contain at least 5 letters.')

try:
    if REQUEST.get('username') and not context.portal_registration.isMemberIdAllowed(REQUEST.get('username')):
        state.setError('username', 'The login name you selected is already in use or is not valid. Please choose another.')
except:
    state.setError('username', context.plone_utils.exceptionString())

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state.set(portal_status_message='You have been registered.')
