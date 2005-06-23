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

try:
    from DateTime.DateTime import DateTimeError
except ImportError:
    DateTimeError = 'DateTimeError'

if updateBase and updateBase!='None':
    try:
        updateBase=DateTime(updateBase)
    except (AttributeError, DateTimeError):
        state.setError('updateBase', 'Please enter a valid date and time.')

if updateFrequency is None:
    state.setError('updateFrequency', 'This field is required, please provide some information.', 'input_required')

if max_items is None:
    state.setError('max_items', 'This field is required, please provide some information.', 'input_required')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.')
    return state.set(status='failure')
else:
    return state
