## Script (Python) "validate_image_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a topic edit_form contents
##
validator = context.portal_form_validation.createForm()
validator.addField('id', 'String', required=1)
validator.addField('title', 'String', required=1)
errors=validator.validate(context.REQUEST)
if errors:
    return ('failure', errors, 'Please correct the indicated errors.')
return ('success', errors, None)

