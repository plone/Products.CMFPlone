## Controller Python Script "validate_event_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates an event edit_form contents
##

from DateTime import DateTime
REQUEST=context.REQUEST

validator = context.portal_form.createForm()
validator.addField('title', 'String', required=1)
validator.addField('start_date', 'String', required=1)
validator.addField('end_date', 'String', required=1)
errors = validator.validate(REQUEST)
for fieldid, error in errors.items():
    state.setError(fieldid, error)

if not state.getError('start_date') and not state.getError('end_date'):
    start_date = None
    try:
        start_date = DateTime(REQUEST.start_date)
    except:
        state.setError('start_date', 'Please enter a valid date and time.')
    end_date = None
    try:
        end_date = DateTime(REQUEST.end_date)
    except:
        state.setError('end_date', 'Please enter a valid date and time.')
    
    if start_date and end_date:
        if start_date.greaterThan(end_date):
            state.setError('end_date', 'An event must end after it starts.')
            state.setError('start_date', 'An event must start before it ends.')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
