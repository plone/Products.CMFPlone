## Script (Python) "mail_password"
##title=Mail a user's password
##parameters=
REQUEST=context.REQUEST
try:
    response = context.portal_registration.mailPassword(REQUEST['userid'], REQUEST)
except 'NotFound':
    REQUEST.set('portal_status_message', 'The User ID you entered could not be found.')
    response = context.mail_password_form()
return response
