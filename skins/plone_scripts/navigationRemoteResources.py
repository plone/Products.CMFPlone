## Script (Python) "navigationRemoteResources"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=encapsulates the related box
##
listing=[]

if obj is None:    
    obj=context
    if not obj.isPrincipiaFolderish:
        obj=obj.aq_parent

try:
    for o in obj.contentValues('Link'):
        listing.append( (o.title_or_id(),
                         o.getRemoteUrl()) )
except: 
    pass
    
return listing
