## Script (Python) "breadcrumbs"
##bind container=
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=used to make the breadcrumbs in the pathbar
##
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized
dynamic_type = "Products.CMFCore.interfaces.Dynamic.DynamicType"

# Some variables
url_tool = getToolByName(context, 'portal_url')
# required for login into a not migrated plone1 site
try:
    iface_tool = getToolByName(context, 'portal_interface')
except AttributeError:
    iface_tool = None

checkPermission=context.portal_membership.checkPermission
dont_show_metatypes = ['TempFolder', # Metatypes of objects we wont show
                       'Plone Factory Tool',
                       'Plone Form Tool']
dont_show = ['talkback'] # Objects we won't show.
                          # Talkback would clutter our precious
                          # breadcrumbs.

portal = url_tool.getPortalObject()


def get_parent(obj, portal):
    if obj == portal:
        return None
    # If the user doesn't have 'Access contents information'
    # at some level, then it will append '...' to breadcrumbs
    # and not present a link to that item.
    try:
        parent = obj.getParentNode()
        # Try to access attribute to see if we have enough
        # permissions to get info about this object.
        getattr(obj, 'meta_type', None)
        return parent
    except Unauthorized:
        # It wasn't possible to get at the parent
        # or at it's attributes. We probably dont
        # have the required permissions, so let's
        # try to skip this object on to the next one.
        subpath = list(url_tool.getRelativeContentPath(current))[:-1]
        while subpath:
            try:
                parent = portal.restrictedTraverse(subpath)
                # Try to access attribute to see if we have enough
                # permissions to get info about this object.
                getattr(parent, 'meta_type', None)
                return parent
            except Unauthorized:
                # Unable to get info. Use '...' for name
                # and dont generate a link.
                path_seq.append(('...', None))
                subpath.pop()
            else:
                break
        # couldn't get parent
        return None


published = context.REQUEST.get('PUBLISHED', None)
published_id = None
if published is not None and hasattr(published, 'getId'):
    published_id = published.getId()

currentlyViewingFolderContents = (published_id in ['folder_contents',
                                                   'folderContents'])
path_seq = []

start = context
if obj is not None:
    start = obj

first_item = 1
if published != start and published_id:
    current = published
    parent = start
    id = published_id
else:
    current = start
    parent = get_parent(current, portal)
    id = None
    if hasattr(current, 'getId'):
        id = current.getId()

# Add breadcrumbs for directories between the root and the published object.
while 1:
    if first_item:
        first_item = 0
        if id is None:
            continue
        # see if the first item in the stack is folder_contents
        if currentlyViewingFolderContents:
            continue
        # see if the first item in the stack is a view
        try:
            if parent is not None:
                if getattr(parent, 'isPrincipiaFolderish', 0):
                    if id in portal.plone_utils.browserDefault(parent)[1]:
                        continue
                if hasattr(parent, 'getTypeInfo'):
                    # The types tool has a getTypeInfo method, but with a 
                    # different signature. http://plone.org/collector/2998
                    try:
                        if id == parent.getTypeInfo().getActionById('view'):
                            continue
                    except TypeError:
                        pass
        except Unauthorized:
            if id in ['view', 'index_html', 'folder_listing']:
                continue
    else:
        current = parent
        if current is None:
            break
        parent = get_parent(current, portal)
        if not hasattr(current, 'getId'):
            continue
        id = current.getId()
        
        # Content objects inherit from DynamicType (except for the portal itself)
        # Make sure the object is either a content object or the portal
        # (Don't do this test on the first object because it could be a page template)
        if current != portal and iface_tool and not iface_tool.objectImplements(current, dynamic_type):
            continue

    if not hasattr(current, 'title_or_id'):
        continue
    
    if id in dont_show:
        continue

    # don't show temporary folders or other excluded types
    if getattr(current, 'meta_type', None) in dont_show_metatypes:
        continue

    url = current.absolute_url()
    title = current.title_or_id()
    if current.isPrincipiaFolderish:
        if (currentlyViewingFolderContents and
            checkPermission('List folder contents', current)):
            path_seq.append((title, url+'/folder_contents'))
        else:
            path_seq.append((title, url+'/'))
    else:
        # We assume in search results everything has a view
        # and if every object is derived from PortalObject, it
        # must have a method called view, so I think its pretty
        # safe to make this assumption, and adds a speed increase
        path_seq.append((title, url+'/view'))

path_seq.reverse()

# If the published object was not added to breadcrumbs above and
#    it is not a view template, add a breadcrumb for it

return path_seq
