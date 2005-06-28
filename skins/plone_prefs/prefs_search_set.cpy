## Controller Script (Python) "prefs_search_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=livesearch=False, RESPONSE=None
##title=Set Search Prefs
##

from Products.CMFCore.utils import getToolByName

REQUEST=context.REQUEST
portal_properties=getToolByName(context, 'portal_properties')


jstool=getToolByName(context, 'portal_javascripts')
jstool.unregisterResource('livesearch.js')

if livesearch:
  portal_properties.site_properties.manage_changeProperties(enable_livesearch=True)
  jstool.registerScript('livesearch.js',enabled=True)
else:
  portal_properties.site_properties.manage_changeProperties(enable_livesearch=False)
  jstool.registerScript('livesearch.js',enabled=False)

msg = 'Search settings updated.' 

return state.set(portal_status_message=msg)
