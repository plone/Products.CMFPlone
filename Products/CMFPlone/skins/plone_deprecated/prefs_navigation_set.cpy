## Controller Script (Python) "prefs_navigation_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=generated_tabs=False, allparents=False, nonfolderish_tabs=False, portaltypes=[], enable_wf_state_filtering=False, wf_states_to_show=[], RESPONSE=None
##title=Set Navigation Prefs
##

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

REQUEST=context.REQUEST
portal_properties=getToolByName(context, 'portal_properties')
plone_utils=getToolByName(context, 'plone_utils')

if generated_tabs:
  portal_properties.site_properties.manage_changeProperties(disable_folder_sections=False)
else:
  portal_properties.site_properties.manage_changeProperties(disable_folder_sections=True)

if allparents:
    portal_properties.navtree_properties.manage_changeProperties(showAllParents=True)
else:
    portal_properties.navtree_properties.manage_changeProperties(showAllParents=False)

if nonfolderish_tabs:
    portal_properties.site_properties.manage_changeProperties(disable_nonfolderish_sections=False)
else:
    portal_properties.site_properties.manage_changeProperties(disable_nonfolderish_sections=True)

# The menu pretends to be a whitelist, but we are storing a blacklist so that
# new types are searchable by default. Inverse the list.
userFriendlyTypes = plone_utils.getUserFriendlyTypes()
allTypes = context.getPortalTypes()
blacklistedTypes = [t for t in allTypes if t not in portaltypes
                                        or t not in userFriendlyTypes]

portal_properties.navtree_properties.manage_changeProperties(
                        metaTypesNotToList=blacklistedTypes,
                        enable_wf_state_filtering=enable_wf_state_filtering,
                        wf_states_to_show=wf_states_to_show)

context.plone_utils.addPortalMessage(_(u'Navigation settings updated.'))
return state
