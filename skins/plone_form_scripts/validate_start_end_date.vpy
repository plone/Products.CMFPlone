## Controller Python Script "validate_event_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=start_date='',end_date=''
##title=Validates an event edit_form contents
##
from DateTime import DateTime

if not start_date:
    state.setError('start_date', 'Input is required but not given.', 'input_required')

if not end_date:
    state.setError('end_date', 'Input is required but not given.', 'input_required') 

if not state.getError('start_date') and not state.getError('end_date'):
    try:
        start_date = DateTime(start_date)
    except TypeError:
        state.setError('start_date', 'Please enter a valid date and time.')

    try:
        end_date = DateTime(end_date)
    except TypeError:
        state.setError('end_date', 'Please enter a valid date and time.')
    
    if start_date and end_date:
        if start_date.greaterThan(end_date):
            state.setError('end_date', 'An event must end after it starts.')
            state.setError('start_date', 'An event must start before it ends.')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
