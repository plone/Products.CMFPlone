## Script (Python) "register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=password='password', confirm='confirm'
##title=Register a User
##
REQUEST=context.REQUEST
portal_registration=context.portal_registration
portal_properties=context.portal_properties

errors=context.validate_registration()
if errors:
    return context.join_form( context, REQUEST)

password=REQUEST.get('field_password') or portal_registration.generatePassword()
portal_registration.addMember(REQUEST['field_username'], password, properties=REQUEST)
if portal_properties.validate_email or REQUEST.get('field_mail_me', 0):
    portal_registration.registeredNotify(REQUEST['field_username'])

return context.registered( context, REQUEST )
