## Script (Python) "validate_metadata_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates an event metadata_edit_form contents
##
from DateTime import DateTime
REQUEST=context.REQUEST

errors = {}

effective_date = None
try:
    if REQUEST.effective_date != 'None' and \
      REQUEST.effective_date != '':
        effective_date = DateTime(REQUEST.effective_date)
except:
    errors['effective_date'] = 'Please enter a valid date and time.'
    
expiration_date = None
try:
    if REQUEST.expiration_date != 'None' and \
      REQUEST.expiration_date != '':
        expiration_date = DateTime(REQUEST.expiration_date)
except:
    errors['expiration_date'] = 'Please enter a valid date and time.'

#if effective_date and expiration_date:
#    if effective_date.greaterThan(expiration_date):
#        errors['expiration_date'] = 'The expiration date must occur after the effective date.'
#        errors['effective_date'] = 'The effective date must occur before the expiration date.'

if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})

return ('success', errors, {})
