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
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    context.plone_utils.addPortalMessage(_(u'You have been registered.'))
    return state
