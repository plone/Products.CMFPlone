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
subjects=None

if obj is None:
    obj=context
    
if hasattr(obj, 'Subject'):
    subjects=obj.Subject()
    
if subjects is not None:  
    for o in context.portal_catalog(Subject = {'query':subjects} ):
        url=o.getURL()
        if url.find(obj.absolute_url())==-1:
            if o.Title:
                listing+=( (o.Title, url), )
return listing
  
