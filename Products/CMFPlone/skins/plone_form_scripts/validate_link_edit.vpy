## Controller Python Script "validate_link_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=remote_url=''
##title=Validate link_edit_form contents
##

from Products.CMFPlone import PloneMessageFactory as _

if not remote_url:
    state.setError('remote_url', _(u'This field is required, please provide some information.'), 'invalid_url')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    context.plone_utils.addPortalMessage(_(u'Your link changes have been saved.'))
    return state
