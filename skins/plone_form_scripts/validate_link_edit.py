## Script (Python) "validate_link_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validate link_edit_form contents
##
validator = context.portal_form.createForm()
validator.addField('title', 'String', required=1)
validator.addField('remote_url', 'String', required=1)
errors = validator.validate(context.REQUEST, context.REQUEST.get('errors', None))
if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
else:
    return ('success', errors, {'portal_status_message':'Your link changes have been saved.'})
