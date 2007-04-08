## Script (Python) "validate_content_status_history"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=workflow_action=''
##title=Validates content publishing
##

from Products.CMFPlone import PloneMessageFactory as _

if not workflow_action:
    state.setError('workflow_action', _(u'This field is required, please provide some information.'), 'workflow_missing')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state

