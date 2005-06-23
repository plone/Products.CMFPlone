## Script (Python) "validate_effective_expiry_date"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=effective_date=None,expiration_date=None
##title=Validates effective,expiration date
##
try:
    from DateTime.DateTime import DateTimeError
except ImportError:
    DateTimeError = 'DateTimeError'

REQUEST=context.REQUEST

try:
    if effective_date and effective_date!='None':
        effective_date = DateTime(effective_date)
except (AttributeError, KeyError, DateTimeError):
    state.setError('effective_date', 'Please enter a valid date and time.')
    REQUEST.set('effective_date', '')   # Remove bad date from request
    
try:
    if expiration_date and expiration_date != 'None':
        expiration_date = DateTime(expiration_date)
except (AttributeError, KeyError, DateTimeError):
    state.setError('expiration_date', 'Please enter a valid date and time.')
    REQUEST.set('expiration_date', '')  # Remove bad date from request

#if effective_date and expiration_date:
#    if effective_date.greaterThan(expiration_date):
#        errors['expiration_date'] = 'The expiration date must occur after the effective date.'
#        errors['effective_date'] = 'The effective date must occur before the expiration date.'

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.')
    return state.set(status='failure')
else:
    return state
