## Script (Python) "validate_personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates the personalization form
##
validator = context.portal_form_validation.createForm()
validator.addField('email', 'Email', required=1)
return validator.validate(context.REQUEST)
