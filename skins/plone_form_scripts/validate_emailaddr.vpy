## Controlled Python Script "validate_emailaddr"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email=''
##title=Validates an email
##
reg_tool=context.portal_registration

def invalid(field):
    state.setError('email', 'You did not enter an email address.', 'invalid_email')

if email and not reg_tool.isValidEmail(email):
    invalid('email')
else:
    invalid('email')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state

