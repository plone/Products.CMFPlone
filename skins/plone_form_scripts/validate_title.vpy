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

if not title:
    state.setError('title', 'This field is required, please provide some information.', 'input_required')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state

