## Script (Python) "validate_topic_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a topic edit_form contents
##
validator = context.portal_form.createForm()
validator.addField('id', 'String', required=1)
validator.addField('title', 'String', required=1)
errors=validator.validate(context.REQUEST)
if errors:
    return state.set(status='failure', errors=errors, portal_status_message='Please correct the indicated errors.')
return state.set(portal_status_message=context.REQUEST.get('portal_status_message', 'Your changes to Topic have been saved.') )
