## Script (Python) "navigationRemoteResources"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=encapsulates the related box
##
listing=()

if obj is None:
    obj=context

if hasattr(obj, 'listFolderContents'):
    for o in obj.listFolderContents():
        if o.Type() == 'Link' and obj.getId()!=o.getId():
            listing+=( (o.title_or_id(), o.getRemoteUrl()), )

return listing
  