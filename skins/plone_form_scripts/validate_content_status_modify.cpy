## Script (Python) "validate_reconfig"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates content publishing
##

from DateTime import DateTime
REQUEST=context.REQUEST
state = context.portal_form_controller.getState(script, is_validator=1)

effective_date = None
try:
    if REQUEST.effective_date != 'None' and \
      REQUEST.effective_date != '':
        effective_date = DateTime(REQUEST.effective_date)
except:
    state.setError('effective_date', 'Please enter a valid date and time.')
    
expiration_date = None
try:
    if REQUEST.expiration_date != 'None' and \
      REQUEST.expiration_date != '':
        expiration_date = DateTime(REQUEST.expiration_date)
except:
    state.setError('expiration_date', 'Please enter a valid date and time.')


validator = context.portal_form.createForm()
validator.addField('workflow_action', 'String', required=1)
errors = validator.validate(context.REQUEST)
for fieldid, error in errors.items():
    state.setError(fieldid, error)

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state

