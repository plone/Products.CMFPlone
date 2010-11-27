## Controlled Python Script "validate_id"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=None
##title=Validates an object id
##

from Products.CMFPlone import PloneMessageFactory as _

# do basic id validation
if id is not None:
    # PloneTool.contentEdit strips the id, so make sure we test the stripped version
    id = id.strip()

id_error = context.check_id(id, 0, None)
if id_error:
    state.setError('id', id_error, new_status='failure')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state

