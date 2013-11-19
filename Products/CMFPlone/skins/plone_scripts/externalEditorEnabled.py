## Script (Python) "externalEditorEnabled"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Can an object be changed with the external editor and by the user

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import webdav_enabled

portal = getToolByName(context, 'portal_url').getPortalObject()
mtool = getToolByName(portal, 'portal_membership')

if mtool.isAnonymousUser():
    return False

# Temporary content cannot be changed through EE (raises AttributeError)
portal_factory = getToolByName(portal, 'portal_factory', None)
if portal_factory and portal_factory.isTemporary(context):
    return False

# Check if the member property
member = mtool.getAuthenticatedMember()
if not member.getProperty('ext_editor', False):
    return False

if not webdav_enabled(context, container):
    return False

# Object not locked ?
# note: you may comment out those two lines if you prefer to let the user to
# borrow the lock
if context.wl_isLocked():
    return False

state = context.restrictedTraverse("@@plone_context_state")
if state.is_structural_folder():
    return False

# Content may provide data to the external editor ?
return not not portal.externalEditLink_(context)
