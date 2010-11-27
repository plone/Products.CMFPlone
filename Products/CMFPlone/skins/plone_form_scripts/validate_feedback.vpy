## Controller Script Python "validate_author_feedback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=referer,subject,message,author=None
##title=validates the form for sending feedback

from Products.CMFPlone import PloneMessageFactory as _
plone_utils=context.plone_utils

if not (subject and subject.strip()):
    state.setError('subject', _(u'Please enter a subject.'), 'email_required')

if not (message and message.strip()):
    state.setError('message', _(u'Please enter a message'), 'email_required')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state
