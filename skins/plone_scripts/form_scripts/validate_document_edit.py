## Script (Python) "validate_document_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a document edit_form contents
##

validator = context.portal_form_validation.createForm()
validator.addField('id', 'String', required=1)
validator.addField('title', 'String', required=1)
errors = validator.validate(context.REQUEST)

file = context.REQUEST.get('file', '')
if file and getattr(file, 'filename' ,''): 
    file.seek(0)
    headers = file.headers
    if headers['Content-Type'].find('text')==-1:
        errors.update( {'file':'This file is not text, To upload binary files create File content,'} )

if errors:
    return ('failure', errors, 'Please correct the indicated errors.')
else:
    return ('success', errors, None)
