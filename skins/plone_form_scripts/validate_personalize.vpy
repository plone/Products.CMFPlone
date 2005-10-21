## Controller Python Script "validate_personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email=''
##title=validates user preferences

from Products.CMFPlone import PloneMessageFactory as _

if state.getErrors():
    return state.set(status='failure', portal_status_message=_(u'Please correct the indicated errors.'))
else:
    return state.set(portal_status_message=_(u'You have been registered.'))
