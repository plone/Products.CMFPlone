## Script (Python) "validate_personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates the personalization form
##
validator = context.portal_form.createForm()
validator.addField('email', 'Email', required=1)
errors=validator.validate(context.REQUEST)
if errors:
    return ('failure', errors, {'portal_status_message':'Please correct your errors'})
return ('success', errors, {'portal_status_message':'Personal settings have been saved'})

