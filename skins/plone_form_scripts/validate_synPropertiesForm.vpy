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

from DateTime import DateTime

if updateBase and updateBase!='None':
    try:
        updateBase=DateTime(updateBase)
    except AttributeError:
        state.setError('updateBase', 'Please enter a valid date and time.')

if updateFrequency is None:
    state.setError('updateFrequency', 'Input is required but no input given.', 'input_required')

if max_items is None:
    state.setError('max_items', 'Input is required but no input given.', 'input_required')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
