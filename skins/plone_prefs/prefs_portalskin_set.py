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

#get cookie name to set it again, if not cookie name is cleared
rv=ps.request_varname

ps.manage_properties(default_skin=default_skin,
                     allow_any=allow_any,
                     cookie_persistence=cookie_persistence
		     request_varname=rv)

msg = 'Portal skin updated'
RESPONSE.redirect('prefs_portalskin_form?portal_status_message=' + msg)

return
