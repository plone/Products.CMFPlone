## Script (Python) "validate_event_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
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

if not errors.get('start_date') and not errors.get('end_date'):
    start_date = None
    try:
        start_date = DateTime(REQUEST.start_date)
    except:
        errors['start_date'] = 'Please enter a valid date and time.'
    end_date = None
    try:
        end_date = DateTime(REQUEST.end_date)
    except:
        errors['end_date'] = 'Please enter a valid date and time.'
    
    if start_date and end_date:
        if start_date.greaterThan(end_date):
            errors['end_date'] = 'An event must end after it starts.'
            errors['start_date'] = 'An event must start before it ends.'

if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})

return ('success', errors, {'portal_status_message':'Your event changes have been saved.'})
