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
if not workflow_action:
    state.setError('workflow_action', 'Input is required but no input given.', 'workflow_missing')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state

