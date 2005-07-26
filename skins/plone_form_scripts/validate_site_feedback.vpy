## Controller Script Python "validate_site_feedback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state  
##bind subpath=traverse_subpath
##parameters=subject,message,sender_from_address,sender_fullname
##title=validates the form for sending feedback

reg_tool=context.portal_registration 

if not sender_from_address:
    state.setError('sender_from_address', 'Please submit an email address.', 'sender_from_address_required')
else:
    if not reg_tool.isValidEmail(sender_from_address):
        state.setError('sender_from_address', 'You entered an invalid email address.', 'invalid_email')
 
if not sender_fullname:
    state.setError('sender_fullname', 'Please enter your name.', 'sender_fullname_required')

if not (subject and subject.strip()):
    state.setError('subject', 'Please enter a subject.', 'subject_required')

if not (message and message.strip()):
    state.setError('message', 'Please enter a message', 'message_required')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
