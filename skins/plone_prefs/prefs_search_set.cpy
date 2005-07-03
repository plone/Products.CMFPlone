## Controller Script (Python) "prefs_search_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=livesearch=False, portaltypes=None, RESPONSE=None
##title=Set Search Prefs
##

from Products.CMFCore.utils import getToolByName

REQUEST=context.REQUEST
portal_properties=getToolByName(context, 'portal_properties')


jstool=getToolByName(context, 'portal_javascripts')

if livesearch:
  portal_properties.site_properties.manage_changeProperties(enable_livesearch=True)
  jstool.getResource('livesearch.js').setEnabled(True)
  jstool.cookResources()
else:
  portal_properties.site_properties.manage_changeProperties(enable_livesearch=False)
  jstool.getResource('livesearch.js').setEnabled(False)
  jstool.cookResources()

portal_properties.site_properties.manage_changeProperties(types_not_searched=portaltypes)

msg = 'Search settings updated.' 

return state.set(portal_status_message=msg)
