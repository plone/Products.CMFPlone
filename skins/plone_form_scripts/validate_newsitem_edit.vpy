## Controller Python Script "validate_newsitem_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title=''
##title=Validates a newsitem edit_form contents
##

from Products.CMFPlone import PloneMessageFactory as _

if not title:
    state.setError('title', _(u'This field is required, please provide some information'), 'input_required')

if state.getErrors():
    return state.set(status='failure', portal_status_message=_(u'Please correct the indicated errors.'))
else:
    return state
