## Controller Script Python "validate_author_feedback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state  
##bind subpath=traverse_subpath
##parameters=author,referer,subject,message
##title=validates the form for sending feedback

plone_utils=context.plone_utils

if not author:
    state.setError('author', 'Please submit an email address.', 'email_required')

if not (subject and subject.strip()):
    state.setError('subject', 'Please enter a subject.', 'email_required')

if not (message and message.strip()):
    state.setError('message', 'Please enter a message', 'email_required')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
