## Controller Script (Python) "prefs_mailhost_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=smtp_server, smtp_port, smtp_userid=None, smtp_pass=None, RESPONSE=None
##title=Set Mailhost Prefs
##

REQUEST=context.REQUEST

mh = context.MailHost

# BBB: Zope 2.7 MailHost objects have no user/password
try:
    mh.manage_makeChanges('Plone Mail Host', smtp_server, smtp_port, smtp_userid, smtp_pass)
except TypeError:
    mh.manage_makeChanges('Plone Mail Host', smtp_server, smtp_port)

msg = 'Mail Host Updated'

return state.set(portal_status_message=msg)
