## Script (Python) "validate_folder_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a folder edit_form contents
##
validator = context.portal_form.createForm()
validator.addField('title', 'String', required=1)
errors=validator.validate(context.REQUEST)
if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
return ('success', errors, {'portal_status_message':'Your folder properties have been saved.'})
