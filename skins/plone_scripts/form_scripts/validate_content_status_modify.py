## Script (Python) "validate_reconfig"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates content publishing
##

validator = context.portal_form.createForm()
validator.addField('effective_date', 'Date', required=0)
validator.addField('expiration_date', 'Date', required=0)
validator.addField('workflow_action', 'String', required=1)
errors = validator.validate(context.REQUEST)
if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
return ('success', errors, {'portal_status_message':'Content publishing information has been saved.'})

