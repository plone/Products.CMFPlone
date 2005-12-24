## Script (Python) "mail_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Mail a user's password
##parameters=
REQUEST=context.REQUEST
try:
    response = context.portal_registration.mailPassword(REQUEST['userid'], REQUEST)
except ValueError, e:
    REQUEST.set('portal_status_message', str(e))
    response = context.mail_password_form()
return response
