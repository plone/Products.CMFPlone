## Controller Python Script "validate_member_portraits"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids=[]
##title=validates the member portraits

if not ids:
   state.setError('ids', 'Input is required but no input given.', 'input_required') 

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state.set(portal_status_message='Member portraits removed.')
