## Script (Python) "validate_link_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a link edit_form contents
##
validator = context.portal_form_validation.createForm()
validator.addField('id', 'String', required=1)
validator.addField('title', 'String', required=1)
validator.addField('remote_url', 'String', required=1)
return validator.validate(context.REQUEST)
