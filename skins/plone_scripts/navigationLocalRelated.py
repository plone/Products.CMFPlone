## Script (Python) "navigationLocalRelated"
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

if hasattr(obj, 'Subject') and obj.Subject(): #shared same metadata  
    for o in context.portal_catalog(Subject={'query':obj.Subject()}):
        url=o.getURL()
        if url.find(obj.absolute_url())==-1:
            if o.Title:
                listing+=( (o.Title, url), )
            else:
                listing+=( (o.id, url), )

return listing
  