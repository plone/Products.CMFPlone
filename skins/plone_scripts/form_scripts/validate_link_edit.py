## Script (Python) "validate_link_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates a link edit_form contents
##
REQUEST=context.REQUEST
fv=context.portal_form_validation

form=fv.createForm()
idField=fv.createField('String', 'id', title='id', required=1, display_width=20)
form.add_field(idField)

titleField=fv.createField('String', 'title', title='title', required=1, display_width=20)
form.add_field(titleField)

remoteUrlField=fv.createField('String', 'remote_url', title='remote_url', required=1, display_width=20)
form.add_field(remoteUrlField)
errors=fv.validate(form)

context.validate_setupRequest(errors) #this could be pushed into validate() method
return errors


