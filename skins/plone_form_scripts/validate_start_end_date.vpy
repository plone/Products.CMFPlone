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
try:
    from DateTime.DateTime import DateTimeError
except ImportError:
    DateTimeError = 'DateTimeError'

REQUEST=context.REQUEST

start_date_year = REQUEST.get('start_date_year',None)
if start_date_year:
    start_date_month = REQUEST.get('start_date_month',None)
    start_date_day = REQUEST.get('start_date_day',None)
    start_date_hour = REQUEST.get('start_date_hour',None)
    start_date_minute = REQUEST.get('start_date_minute',None)

    if start_date_month and start_date_day and start_date_hour and start_date_minute:
         start_date='%s-%s-%s %s:%s'%(start_date_year,start_date_month,start_date_day,start_date_hour,start_date_minute)

end_date_year = REQUEST.get('end_date_year', None)
if end_date_year:
    end_date_month = REQUEST.get('end_date_month',None)
    end_date_day = REQUEST.get('end_date_day', None)
    end_date_hour = REQUEST.get('end_date_hour', None)
    end_date_minute = REQUEST.get('end_date_minute',None)

    if end_date_month and end_date_day and end_date_hour and end_date_minute:
         end_date='%s-%s-%s %s:%s'%(end_date_year,end_date_month,end_date_day,end_date_hour,end_date_minute)

if not start_date:
     state.setError('start_date', 'Input is required but not given.', 'input_required')

if not end_date:
     state.setError('end_date', 'Input is required but not given.', 'input_required')

if not state.getError('start_date') and not state.getError('end_date'):
    tmp_start_date = None
    tmp_end_date = None

    try:
        tmp_start_date = DateTime(start_date)
    except (TypeError, DateTimeError):
        state.setError('start_date', 'Please enter a valid date and time.')
        REQUEST.set('start_date', '')   # Remove bad date from request

    try:
        tmp_end_date = DateTime(end_date)
    except (TypeError, DateTimeError):
        state.setError('end_date', 'Please enter a valid date and time.')
        REQUEST.set('end_date', '')     # Remove bad date from request

    if tmp_start_date and tmp_end_date:
        if tmp_start_date.greaterThan(tmp_end_date):
            state.setError('end_date', 'An event must end after it starts.')
            state.setError('start_date', 'An event must start before it ends.')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    REQUEST.set('start_date',start_date)
    REQUEST.set('end_date',end_date)
    return state
