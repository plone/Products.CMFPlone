## Controller Python Script "validate_newsitem_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title=''
##title=Validates a newsitem edit_form contents
##

if not title:
    state.setError('title', 'This field is required, please provide some information', 'input_required')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.')
    return state.set(status='failure')
else:
    return state
