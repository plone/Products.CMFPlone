## Script (Python) "navigationCurrent"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None
##title=encapsulates the current and up one level box contents
##
listing=()

if obj is None: 
    obj=context 

if not obj.isPrincipiaFolderish: 
    obj=obj.aq_parent

try:
    for o in obj.listFolderContents(spec='Folder'):
       if o.Type()=='Folder' and o.Title()!='Favorites':
           if context.portal_membership.checkPermission('List folder contents', o):
               listing += (o,)
       else:
           if o.getId() != context.getId():
               listing += (o,)
    
except: #CMF is not catching its own exceptions, as advertised
    pass

return listing
