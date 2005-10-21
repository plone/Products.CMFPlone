## Script (Python) "prefs_portalskin_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=default_skin, allow_any=0, cookie_persistence=0, RESPONSE=None
##title=set portalskin prefs
##

from Products.CMFPlone import PloneMessageFactory as _
REQUEST=context.REQUEST

ps = context.portal_skins

#get cookie name to set it again, if no cookie name is set,
#set it to defaul value. else cookie name is cleared which
#causes login errors
if ps.request_varname:
    rv=ps.request_varname
else:
    rv='plone_skin'

ps.manage_properties(default_skin=default_skin,
                     allow_any=allow_any,
                     cookie_persistence=cookie_persistence,
                     request_varname=rv)

return state.set(portal_status_message=_(u'Portal skin updated'))
