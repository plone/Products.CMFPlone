## Script (Python) "validate_newsitem_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a newsitem edit_form contents
##
validator = context.portal_form.createForm()
validator.addField('title', 'String', required=1, required_not_found='Please enter a title.')
errors = validator.validate(context.REQUEST)

if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
else:
    return ('success', errors, {})
        
