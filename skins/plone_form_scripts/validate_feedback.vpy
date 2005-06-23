## Controller Script Python "validate_author_feedback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state  
##bind subpath=traverse_subpath
##parameters=referer,subject,message,author=None
##title=validates the form for sending feedback

plone_utils=context.plone_utils

#if not author:
#    state.setError('author', 'Please submit an email address.', 'email_required')

if not (subject and subject.strip()):
    state.setError('subject', 'Please enter a subject.', 'email_required')

if not (message and message.strip()):
    state.setError('message', 'Please enter a message', 'email_required')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.')
    return state.set(status='failure')
else:
    return state
