## Controlled Python Script "validate_id"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None
##title=Validates an object id
##
state = context.portal_form_controller.getState(script, is_validator=1)

# do basic id validation
if id is not None:
    # PloneTool.contentEdit strips the id, so make sure we test the stripped version
    id = id.strip() 

id_error = context.check_id(id, 0, None)
if id_error:
    state.setError('id', id_error, new_status='failure')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state

