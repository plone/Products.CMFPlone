## Script (Python) "validate_reconfig"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates CMF Site reconfig form
##
state = context.portal_form_controller.getState(script, is_validator=1)

validator = context.portal_form.createForm()

validator.addField('title', 'String', required=1)
validator.addField('localTimeFormat', 'String', required=1)
validator.addField('localLongTimeFormat', 'String', required=1)
validator.addField('description', 'String', required=0)
validator.addField('email_from_name', 'String', required=0)
validator.addField('email_from_address', 'Email', required=0)
validator.addField('smtp_server', 'String', required=0)

errors = validator.validate(context.REQUEST)
for fieldid, error in errors.items():
    state.setError(fieldid, error)

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
