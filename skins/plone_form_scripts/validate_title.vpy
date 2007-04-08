## Controlled Python Script "validate_title"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title=''
##title=Validates an object title
##

from Products.CMFPlone import PloneMessageFactory as _

if not title:
    state.setError('title', _(u'This field is required, please provide some information.'), 'input_required')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state

