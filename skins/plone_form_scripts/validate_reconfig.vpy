## Controller Python Script "validate_reconfig"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates the portal config

from Products.CMFPlone import PloneMessageFactory as _

# nothing to check?
#if state.getErrors():
#    return state.set(status='failure', portal_status_message=_(u'Please correct the indicated errors.'))
return state
