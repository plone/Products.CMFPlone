## Script (Python) "validate_synPropertiesForm"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates syndication form
##

from DateTime import DateTime
REQUEST=context.REQUEST

errors = {}

updateBase = None
try:
    if REQUEST.updateBase != 'None' and \
      REQUEST.updateBase != '':
        updateBase = DateTime(REQUEST.updateBase)
except:
    errors['updateBase'] = 'Please enter a valid date and time.'
    
validator = context.portal_form.createForm()
validator.addField('updateFrequency', 'Integer', required=1)
validator.addField('max_items', 'Integer', required=1)
errors.update(validator.validate(context.REQUEST))

if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
return ('success', errors, {'portal_status_message':'Syndication information has been saved.'})

