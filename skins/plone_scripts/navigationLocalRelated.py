## Script (Python) "navigationLocalRelated"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=encapsulates the related box
##

related=[]
subjects=None

if obj is None:
    obj=context
    
if hasattr(obj.aq_explicit, 'Subject'):
    subjects=obj.Subject()
    
if subjects:  
    for o in context.portal_catalog( Subject = subjects
                                   , review_state = 'published'
                                   , sort_on = 'portal_type'
                                   , sort_order = 'reverse'  ):
        url=o.getURL()
        title=''
        if url.find(obj.absolute_url())==-1: #we need UIDs
            if o.Title:
                title=o.Title
            else:
                title=o.getId #getId() is indexed as the getId property
            related.append( {'title':title
                            ,'url':url
                            ,'icon':o.getIcon} )
                            
return related

