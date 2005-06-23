## Controller Python Script "validate_metadata_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates metadata screen

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.')
    return state.set(status='failure')
else:
    context.plone_utils.addPortalMessage('You have been registered.')
    return state
