## Controller Script Python "validate_site_feedback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state  
##bind subpath=traverse_subpath
##parameters=subject,message,sender_from_address,sender_fullname
##title=validates the form for sending feedback

if not sender_from_address:
    state.setError('sender_from_address', 'Please submit an email address.', 'email_required')

if not sender_fullname:
    state.setError('sender_fullname', 'Please enter your name.', 'email_required')

if not (subject and subject.strip()):
    state.setError('subject', 'Please enter a subject.', 'email_required')

if not (message and message.strip()):
    state.setError('message', 'Please enter a message', 'email_required')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
