## Controller Script Python "validate_sendto"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=validates the email adresses
state = context.portal_form_controller.getState(script, is_validator=1)
REQUEST=context.REQUEST

validator = context.portal_form.createForm()
validator.addField('send_to_address'  , 'Email', required=1, required_not_found='Please submit an email address.')
validator.addField('send_from_address', 'Email', required=1, required_not_found='Please submit an email address.')
errors = validator.validate(REQUEST, REQUEST.get('errors', None))
for fieldid, error in errors.items():
    state.setError(fieldid, error)

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
