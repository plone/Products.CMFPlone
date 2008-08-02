## Script (Python) "navigationCurrent"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=encapsulates the current and up one level box contents
##a

context.plone_log("The navigationCurrent script is deprecated and will be "
                  "removed in Plone 4.0.")

checkPermission=context.portal_membership.checkPermission

listing=[]
folder=None
if obj is None:
    obj=context

path_ids=context.portal_url.getRelativeContentPath(obj)

if len(path_ids)>1:
    folder=obj.getParentNode()
else:
    folder=context.portal_url.getPortalObject()

if checkPermission('List folder contents', folder):
    for o in folder.listFolderContents():
        if o.getId()=='Folder' and o.Title()!='Favorites':
            if checkPermission('List folder contents', o):
                listing.append(o)
        else:
            listing.append(o)

return listing
