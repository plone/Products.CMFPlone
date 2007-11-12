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

from Products.CMFPlone import PloneMessageFactory as _
from DateTime.DateTime import DateTimeError

REQUEST=context.REQUEST

try:
    if effective_date and effective_date!='None':
        effective_date = DateTime(effective_date)
except (AttributeError, KeyError, DateTimeError):
    state.setError('effective_date', _(u'Please enter a valid date and time.'))
    REQUEST.set('effective_date', '')   # Remove bad date from request
    
try:
    if expiration_date and expiration_date != 'None':
        expiration_date = DateTime(expiration_date)
except (AttributeError, KeyError, DateTimeError):
    state.setError('expiration_date', _(u'Please enter a valid date and time.'))
    REQUEST.set('expiration_date', '')  # Remove bad date from request

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state
