## Script (Python) "prefs_mailhost_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=smtp_server, smtp_port, RESPONSE=None
##title=set mailhost prefs
##

REQUEST=context.REQUEST

mh = context.MailHost

mh.manage_makeChanges('Plone Mail Host', smtp_server ,smtp_port)

msg = 'MailHost %s updated' % mh.id
RESPONSE.redirect('prefs_mailhost_form?portal_status_message=' + msg)

return

