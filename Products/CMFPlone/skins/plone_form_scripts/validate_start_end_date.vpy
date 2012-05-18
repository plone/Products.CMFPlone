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

from Products.CMFPlone import PloneMessageFactory as _
from DateTime.interfaces import DateTimeError

REQUEST=context.REQUEST

if not start_date:
     state.setError('start_date', _(u'Input is required but not given.'), 'input_required')

if not end_date:
     state.setError('end_date', _(u'Input is required but not given.'), 'input_required')

if not state.getError('start_date') and not state.getError('end_date'):
    tmp_start_date = None
    tmp_end_date = None

    try:
        tmp_start_date = DateTime(start_date)
    except (TypeError, DateTimeError):
        state.setError('start_date', _(u'Please enter a valid date and time.'))
        REQUEST.set('start_date', '')   # Remove bad date from request

    try:
        tmp_end_date = DateTime(end_date)
    except (TypeError, DateTimeError):
        state.setError('end_date', _(u'Please enter a valid date and time.'))
        REQUEST.set('end_date', '')     # Remove bad date from request

    if tmp_start_date and tmp_end_date:
        if tmp_start_date.greaterThan(tmp_end_date):
            state.setError('end_date', _(u'An event must end after it starts.'))
            state.setError('start_date', _(u'An event must start before it ends.'))

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    REQUEST.set('start_date',start_date)
    REQUEST.set('end_date',end_date)
    return state
