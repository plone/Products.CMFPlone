## Script (Python) "validate_file_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a file edit_form contents
##

validator = context.portal_form_validation.createForm()
validator.addField('id', 'String', required=1)
validator.addField('title', 'String', required=0)
errors = validator.validate(context.REQUEST)

filename=getattr(context.REQUEST['file'], 'filename', None)
size=context.get_size()
if not filename and not size:
    errors['file']='You must upload a file'

if errors:
    return ('failure', errors, 'Please correct the indicated errors.')
return ('success', errors, None)
