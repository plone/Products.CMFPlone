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

if obj is not None:
    context = obj

# Some variables
url_tool = getToolByName(context, 'portal_url')
# required for login into a not migrated plone1 site
try:
    iface_tool = getToolByName(context, 'portal_interface')
except AttributeError:    
    iface_tool = None

published = context.REQUEST.get('PUBLISHED', None)
published_id = None
checkPermission=context.portal_membership.checkPermission
dont_show_metatypes = ['TempFolder', # Metatypes of objects we wont show
                       'Plone Factory Tool',
                       'Plone Form Tool']
dont_show = ['talkback'] # Objects we won't show.
                          # Talkback would clutter our precious
                          # breadcrumbs.

portal = url_tool.getPortalObject()

if published is not None and hasattr(published, 'getId'):
    published_id = published.getId()

currentlyViewingFolderContents = (published_id in ['folder_contents',
                                                   'folderContents'])
path_seq = []
subpath = []

#o = current = published or context
o = current = context
first_object = 1

# Add breadcrumbs for directories between the root and the published object.
while current and current is not portal:
    if not first_object:
        # If the user doesn't have 'Access contents information'
        # at some level, then it will append '...' to breadcrumbs
        # and not present a link to that item.
        try:
            o = current.getParentNode()
            # Try to access attribute to see if we have enough
            # permissions to get info about this object.
            getattr(o, 'meta_type', None)
        except Unauthorized:
            # It wasn't possible to get at the parent
            # or at it's attributes. We probably dont
            # have the required permissions, so let's
            # try to skip this object on to the next one.
            subpath = list(url_tool.getRelativeContentPath(current))[:-1]
            while subpath:
                try:
                    o = portal.restrictedTraverse(subpath)
                    # Try to access attribute to see if we have enough
                    # permissions to get info about this object.
                    getattr(o, 'meta_type', None)
                except Unauthorized:
                    # Unable to get info. Use '...' for name
                    # and dont generate a link.
                    path_seq.append(('...', None))
                    subpath.pop()
                else:
                    break
            if o is current:
                # Uhm. We are still at the same object,
                # so trying to get a parent failed. Break
                # the loop.
                break
        current = o
    else:
        first_object = 0

    id = o.getId()
    if id in dont_show:
        continue

    # don't show temporary folders or other excluded types
    if getattr(o, 'meta_type', None) in dont_show_metatypes:
        continue

    # Content objects inherit from DynamicType (except for the portal itself)
    # Make sure the object is either a content object or the portal
    if current != portal and iface_tool and not iface_tool.objectImplements(o, dynamic_type):
        continue

    # Special treatment for the context object of the breadcrumb script:
    # We don't want to show a crumb if the current object is the default
    # view for a folder
    if current == context:
        try:
            parent = current.getParentNode()
            if parent.isPrincipiaFolderish:
                browser_default = getattr(parent, 'browserDefault', None)
                if browser_default and callable(browser_default):
                    if current.getId() in browser_default()[1]:
                        continue
        except Unauthorized:
            if current.getId() in ['index_html', 'folder_listing']:
                continue

    url = o.absolute_url()
    title = o.title_or_id()
    if o.isPrincipiaFolderish:
        if (currentlyViewingFolderContents and
            checkPermission('List folder contents', o)):
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

# Under some circunstances (read ZWiki :P) 'published' may
# be a method. A method doesn't have title_or_id, and even if it had
# it would not be accessible from here.

if published != o and iface_tool and \
   iface_tool.objectImplements(published, dynamic_type) and not \
    currentlyViewingFolderContents and \
    published_id not in  ('view', 'index_html') and \
    hasattr(published, 'title_or_id'):
    url = published.absolute_url() + '/view'
    path_seq.append( (published.title_or_id(), url) )

return path_seq