## Controller Python Script "validate_metadata_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates metadata screen

from Products.CMFPlone import PloneMessageFactory as _

if state.getErrors():
    return state.set(status='failure', portal_status_message=_(u'Please correct the indicated errors.'))
else:
    return state.set(portal_status_message=_(u'You have been registered.'))
