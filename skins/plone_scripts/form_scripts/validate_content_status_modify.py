## Script (Python) "validate_reconfig"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates content publishing
##

from DateTime import DateTime
REQUEST=context.REQUEST

errors = {}

effective_date = None
try:
    if REQUEST.effective_date != 'None' and \
      REQUEST.effective_date != '':
        effective_date = DateTime(REQUEST.effective_date)
except:
    errors['effective_date'] = 'Please enter a valid date and time.'
    
expiration_date = None
try:
    if REQUEST.expiration_date != 'None' and \
      REQUEST.expiration_date != '':
        expiration_date = DateTime(REQUEST.expiration_date)
except:
    errors['expiration_date'] = 'Please enter a valid date and time.'


validator = context.portal_form.createForm()
validator.addField('workflow_action', 'String', required=1)
errors.update(validator.validate(context.REQUEST))

if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
return ('success', errors, {'portal_status_message':'Content publishing information has been saved.'})

