## Script (Python) "validate_registration"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=validates the Registration of a User
REQUEST=context.REQUEST

validator = context.portal_form.createForm()
validator.addField('username', 'String', required=1)
validator.addField('email', 'Email')
properties = context.portal_properties.site_properties

if not properties.validate_email:
    # if we are validating email we aren't letting people pick their own passwords.
    validator.addField('password', 'Password', required=1)
    validator.addField('confirm', 'Password', required=1)

errors = validator.validate(REQUEST, REQUEST.get('errors', None))
password, confirm = REQUEST.get('password', ''), REQUEST.get('confirm', '')

#manual validation ;(
if not properties.validate_email:
    if password!=confirm:
        errors['password'] = errors['confirm'] = 'Passwords do not match.'
    if not errors.get('password', None) and len(password) < 5:
        errors['password'] = errors['confirm'] = 'Passwords must contain at least 5 letters.'

#
#
#
try:
    failMessage = context.portal_registration.testPropertiesValidity(REQUEST)
    if failMessage:
        errors['username'] = failMessage

    if not context.portal_registration.isMemberIdAllowed(REQUEST.get('username')):
        errors['username'] = 'This member id is invalid or already in use.'
except:
    errors['username'] = context.plone_utils.exceptionString()

if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
else:
    return ('success', errors, {'portal_status_message':'You have been registered.'})
