## Controller Python Script "validate_synPropertiesForm"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates syndication form
##

from DateTime import DateTime
REQUEST=context.REQUEST

updateBase = None
try:
    if REQUEST.updateBase != 'None' and REQUEST.updateBase != '':
        updateBase = DateTime(REQUEST.updateBase)
except:
    # note necessary evil, DateTime can raise many different errors
    state.setError('updateBase', 'Please enter a valid date and time.')

validator = context.portal_form.createForm()
validator.addField('updateFrequency', 'Integer', required=1)
validator.addField('max_items', 'Integer', required=1)
errors=validator.validate(context.REQUEST)
for fieldid, error in errors.items():
    state.setError(fieldid, error)

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
