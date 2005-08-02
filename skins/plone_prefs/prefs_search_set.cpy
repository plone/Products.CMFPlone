## Controller Script (Python) "prefs_search_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=enable_livesearch=False, portaltypes=[], RESPONSE=None
##title=Set Search Prefs
##

from Products.CMFCore.utils import getToolByName

REQUEST=context.REQUEST
portal_properties=getToolByName(context, 'portal_properties')


jstool=getToolByName(context, 'portal_javascripts')

if enable_livesearch:
  portal_properties.site_properties.manage_changeProperties(enable_livesearch=True)
  jstool.getResource('livesearch.js').setEnabled(True)
  jstool.cookResources()
else:
  portal_properties.site_properties.manage_changeProperties(enable_livesearch=False)
  jstool.getResource('livesearch.js').setEnabled(False)
  jstool.cookResources()

# The menu pretends to be a whitelist, but we are storing a blacklist so that
# new types are searchable by default. Inverse the list.
allTypes = context.getPortalTypes()
blacklistedTypes = [t for t in allTypes if t not in portaltypes]

portal_properties.site_properties.manage_changeProperties(types_not_searched=blacklistedTypes)

msg = 'Search settings updated.'

return state.set(portal_status_message=msg)
