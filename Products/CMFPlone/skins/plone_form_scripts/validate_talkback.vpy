## Controller Script Python "validate_talkback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=subject='',body_text=''
##title=validates a discussion entry

from Products.CMFPlone import PloneMessageFactory as _

dtool = context.portal_discussion
try:
    content = context.parentsInThread()[0]
except AttributeError:
    content = context
if not dtool.isDiscussionAllowedFor(content):
    raise Exception, "Discussion not allowed."

if not subject:
    state.setError('subject', _(u'Subject cannot be blank.'), 'subject_required')

if not body_text:
    state.setError('body_text', _(u'Comment cannot be blank.'), 'body_required')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state
