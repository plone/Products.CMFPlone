## Script (Python) "visibleIdsEnabled"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.plone_log("The visibleIdsEnabled script is deprecated and will be "
                  "removed in plone 3.5.  Use the visibleIdsEnabled method "
                  "of the @@plone view instead.")
props = context.portal_properties.site_properties

if not props.getProperty('visible_ids', False):
    return False

pm=context.portal_membership

if pm.isAnonymousUser():
    return False

user = pm.getAuthenticatedMember()

if user is not None:
    return user.getProperty('visible_ids', False)

return False
