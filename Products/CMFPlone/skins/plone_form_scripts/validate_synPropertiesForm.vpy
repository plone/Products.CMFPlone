## Controller Python Script "validate_synPropertiesForm"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=updateBase=None,updateFrequency=None,max_items=None
##title=Validates syndication form
##

from Products.CMFPlone import PloneMessageFactory as _
from DateTime.interfaces import DateTimeError

if updateBase and updateBase!='None':
    try:
        updateBase=DateTime(updateBase)
    except (AttributeError, DateTimeError):
        state.setError('updateBase', _(u'Please enter a valid date and time.'))

if updateFrequency is None:
    state.setError('updateFrequency', _(u'This field is required, please provide some information.'), 'input_required')

if max_items is None:
    state.setError('max_items', _(u'This field is required, please provide some information.'), 'input_required')

if max_items < 1:
    state.setError('max_items', _(u'The value of this field must be 1 or greater.'))

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state
