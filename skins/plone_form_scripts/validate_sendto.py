## Script (Python) "validate_sendto"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=validates the email adresses
REQUEST=context.REQUEST

validator = context.portal_form.createForm()
validator.addField('send_to_address'  , 'Email', required=1, required_not_found='Please submit an email address.')
validator.addField('send_from_address', 'Email', required=1, required_not_found='Please submit an email address.')

errors = validator.validate(REQUEST, REQUEST.get('errors', None))

if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
else:
    return ('success', errors, {})