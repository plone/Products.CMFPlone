## Script (Python) "validate_newsitem_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a newsitem edit_form contents
##
validator = context.portal_form_validation.createForm()
validator.addField('id', 'String', required=1)
validator.addField('title', 'String', required=1, required_not_found='Please enter a title.')
return validator.validate(context.REQUEST)
