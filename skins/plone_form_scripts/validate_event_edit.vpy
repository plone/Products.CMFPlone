## Controller Python Script "validate_event_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates an event edit_form contents
##

from Products.CMFPlone import PloneMessageFactory as _

if state.getErrors():
    return state.set(status='failure', portal_status_message=_(u'Please correct the indicated errors.'))
else:
    return state
