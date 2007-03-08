## Script (Python) "externalEditorEnabled" 
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Can an object be changed with the external editor and by the user
##
#
from Products.CMFCore.utils import getToolByInterfaceName
from Products.CMFPlone.utils import webdav_enabled

portal = getToolByInterfaceName('Products.CMFCore.interfaces.IURLTool').getPortalObject()
mtool = getToolByInterfaceName('Products.CMFCore.interfaces.IMembershipTool')

if mtool.isAnonymousUser():
    return False

# Temporary content cannot be changed through EE (raises AttributeError)
portal_factory = getToolByInterfaceName('Products.CMFPlone.interfaces.IFactoryTool')
if portal_factory.isTemporary(context):
    return False

# Check if the member property
member = mtool.getAuthenticatedMember()
if not member.getProperty('ext_editor', False):
    return False

if not webdav_enabled(context, container):
    return False

# Object not locked ?
# note: you may comment out those two lines if you prefer to let the user to borrow the lock
if context.wl_isLocked():
    return False

# Content may provide data to the external editor ?
return not not portal.externalEditLink_(context)
