## Script (Python) "validate_image_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates image_edit_form contents
##
validator = context.portal_form.createForm()
validator.addField('title', 'String', required=0)
errors = validator.validate(context.REQUEST)

filename=getattr(context.REQUEST['file'], 'filename', None)
size = 0
if hasattr(context, 'get_size'):  # make sure things work with portal_factory
    size=context.get_size()
if not filename and not size:
    errors['file']='You must upload a file'

if context.CreationDate() == context.ModificationDate() and filename:
    alternative_id = filename[max( string.rfind(filename, '/')
                       , string.rfind(filename, '\\')
                       , string.rfind(filename, ':') )+1:].strip()
else:
    alternative_id = context.getId()

id = context.REQUEST.get('id', '').strip()
id_err = context.check_id(id, 1, alternative_id)
if id_err:
    errors['id'] = id_err

if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
return ('success', errors, {'portal_status_message':'Your image has been saved.'})