## Script (Python) "validate_document_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a document edit_form contents
##

validator = context.portal_form.createForm()
validator.addField('title', 'String', required=1)
errors = validator.validate(context.REQUEST)

file = context.REQUEST.get('file', '')
filename = getattr(file, 'filename' ,'')
if file and filename:
    file.seek(0)
    headers = file.headers
    if headers['Content-Type'].find('text')==-1:
        errors.update( {'file':'This file is not text, To upload binary files create File content,'} )

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
return ('success', errors, {'portal_status_message':'Your document changes have been saved.'})
