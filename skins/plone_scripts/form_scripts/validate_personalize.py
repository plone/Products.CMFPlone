## Script (Python) "validate_personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validates the personalization form
##
REQUEST=context.REQUEST
fv=context.portal_form_validation

form=fv.createForm()
emailField=fv.createField('Email', 'email', title='email', required=1, display_width=20)
form.add_field(emailField)

errors=fv.validate(form)
context.validate_setupRequest(errors) #this could be pushed into validate() method
return errors
