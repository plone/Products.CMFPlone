## Script (Python) "validate_folder_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a folder edit_form contents
##
REQUEST=context.REQUEST
fv=context.portal_form_validation

form=fv.createForm()
idField=fv.createField('String', 'id', title='id', required=1, display_width=20)
form.add_field(idField)

titleField=fv.createField('String', 'title', title='title', required=1, display_width=20)
form.add_field(titleField)
errors=fv.validate(form) #the validate method could just as well setup the next request

context.validate_setupRequest(errors) #setup the Next Request
return errors
