## Controller Script Python "validate_sendto"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=send_to_address='',send_from_address=''
##title=validates the email adresses
if not send_to_address:
    state.setError('send_to_address', 'Please submit an email address.', 'email_required')

if not send_from_address:
    state.setError('send_from_address', 'Please submit an email address.', 'email_required')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
