## Script (Python) "navigationParent"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None,templateId=None,fallThroughDefaultPage=True,checkPermissions=[]
##title=Returns the appropriate url for the parent object
##

# - If obj is given, use this as the object to find the parent of, else
# use the context.
#
# - If fallThroughDefaultPage is set to True (default), then if obj/context is
# the default page (index_html or default_page) of its parent folder, get the
# parent of that folder. If you intend to link straight to the returned value
# this is probably what you want - else Zope will show the parent object, which
# will in turn show obj again (as it is the default page). However, if you
# intend to append a page template to the link, set this to false to get the
# "real" parent. folder_contents does this.
#
# - If you want to make sure that the current user has permissions other than
# "View" on the parent object, pass these in as a list in checkPermissions.
# folder_contents uses this to check the "List folder contents" permission,
# for example.
#
# - templateId is for historical reasons, ignored
#
# Returns the absolute url to the parent object, or None if it cannot be
# found or accessed

from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName, getUtilityByInterfaceName
from AccessControl import Unauthorized

portal = getUtilityByInterfaceName('Products.CMFCore.interfaces.ISiteRoot')
plone_utils = getToolByName(context, 'plone_utils')
portal_membership = getToolByName(context, 'portal_membership')

if obj is None:
    obj = context

checkPermission = portal_membership.checkPermission

if fallThroughDefaultPage:
    # In the case that we have an index_html inside and index_html,
    # we actually need to go the ultimate non-default parent
    try:
        while obj is not None and plone_utils.isDefaultPage(obj):
            obj = obj.aq_parent
    except Unauthorized:
        return None

# Abort if we are at the root of the portal
if obj.getPhysicalPath() == portal.getPhysicalPath():
    return None

# Get the parent. If we can't get it (unauthorized), use the portal
try:
    parent = obj.aq_parent
except ConflictError:
    raise
except:
    return None

# We may get an unauthorized exception if we're not allowed to access#
# the parent. In this case, return None
try:
    if getattr(parent, 'getId', None) is None or \
           parent.getId() == 'talkback':
        # Skip any Z3 views that may be in the acq tree;
        # Skip past the talkback container if that's where we are
        parent = parent.aq_parent

    for perm in checkPermissions:
        if not checkPermission(perm, parent):
            return None

    return parent.absolute_url()

except Unauthorized:
    return None
