## Script (Python) "validate_reconfig"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates CMF Site reconfig form
##

validator = context.portal_form.createForm()

validator.addField('title', 'String', required=1)
validator.addField('localTimeFormat', 'String', required=1)
validator.addField('localLongTimeFormat', 'String', required=1)
validator.addField('description', 'String', required=0)
validator.addField('email_from_name', 'String', required=0)
validator.addField('email_from_address', 'Email', required=0)
validator.addField('smtp_server', 'String', required=0)

errors = validator.validate(context.REQUEST)
if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
return ('success', errors, {'portal_status_message':'Plone setup changes have been saved.'})

