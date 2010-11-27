## Controller Script Python "validate_site_feedback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=subject,message,sender_from_address
##title=validates the form for sending feedback

from Products.CMFPlone import PloneMessageFactory as _
reg_tool=context.portal_registration

if not sender_from_address:
    state.setError('sender_from_address', _(u'Please submit an email address.'), 'sender_from_address_required')
else:
    if reg_tool.isValidEmail(sender_from_address):
        pass
    else:
        state.setError('sender_from_address', _(u'You entered an invalid email address.'), 'invalid_email')

if not (subject and subject.strip()):
    state.setError('subject', _(u'Please enter a subject.'), 'subject_required')

if not (message and message.strip()):
    state.setError('message', _(u'Please enter a message'), 'message_required')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state
