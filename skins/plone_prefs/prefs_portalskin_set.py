## Script (Python) "prefs_portalskin_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=default_skin, allow_any=0, cookie_persistence=0, RESPONSE=None
##title=set portalskin prefs
##

REQUEST=context.REQUEST

ps = context.portal_skins

ps.manage_properties(default_skin=default_skin,
                     request_varname='',
                     chosen=(),
                     add_skin=0,
                     del_skin=0,
                     skinname='',
                     skinpath='',
                     allow_any=allow_any,
                     cookie_persistence=cookie_persistence)

msg = 'Portal skin updated'
RESPONSE.redirect('prefs_portalskin_form?portal_status_message=' + msg)

return
