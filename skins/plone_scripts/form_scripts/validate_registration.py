## Script (Python) "validate_registration"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=validates teh Registration of a User
REQUEST=context.REQUEST
failMessage = None
portal_properties = context.portal_properties
portal_registration = context.portal_registration
vf=context.portal_form_validation
password, confirm = REQUEST.get('field_password', ''), REQUEST.get('field_confirm', '')

form=vf.createForm()

usernameField=vf.createField('String', 'username', title='username', required=1)
form.add_field(usernameField)

emailField=vf.createField('Email', 'email', title='email')
form.add_field(emailField)

if not context.portal_properties.validate_email:
    #if we are validating email we arent letting people pick their own passwords.
    passwordField=vf.createField('Password', 'password', title='password', required=1, display_width=20, minimum_width=5)
    form.add_field(passwordField)

    confirmField=vf.createField('Password', 'confirm', title='confirm', required=1, display_width=20, minimum_width=5)
    form.add_field(confirmField)

errors=vf.validate(form)
if not errors: errors = {}

#manual validation ;(
if not portal_properties.validate_email:
  if password!=confirm:
      errors['password'] = errors['confirm'] = 'Passwords do not match.'
  if not errors.get('password', None) and \
     len(password)<5:
      errors['password'] = errors['confirm'] = 'Password must be atleast 5 letters.'

context.validate_stripPrefixes()

failMessage=portal_registration.testPropertiesValidity(REQUEST)
if failMessage:
    errors['username']=failMessage

if not portal_registration.isMemberIdAllowed(REQUEST.get('field_username')):
    errors['username']='This member id is invalid or already in use.'

context.validate_storeErrors(errors)
return errors
