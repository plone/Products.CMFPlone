## Script (Python) "validate_document_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=file=None
##title=Validates a document edit_form contents
##
REQUEST=context.REQUEST

fv=context.portal_form_validation

form=fv.createForm()
idField=fv.createField('String', 'id', title='id', required=1, display_width=20)
form.add_field(idField)

titleField=fv.createField('String', 'title', title='title', required=1, display_width=20)
form.add_field(titleField)
errors=fv.validate(form)

if file and getattr(file, 'filename' ,''): 
    file.seek(0)
    headers = file.headers
    if headers['Content-Type'].find('text')==-1:
        if not errors: errors={} 
	errors.update( {'file':'This file is not text, To upload binary files create File content,'} )
	    
context.validate_setupRequest(errors)
return errors
