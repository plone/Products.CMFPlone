## Controller Python Script "validate_link_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validate link_edit_form contents
##

validator = context.portal_form.createForm()
validator.addField('title', 'String', required=1)
validator.addField('remote_url', 'String', required=1)
errors = validator.validate(context.REQUEST)
for fieldid, error in errors.items():
    state.setError(fieldid, error, new_status='failure')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state.set(portal_status_message='Your link changes have been saved.')
