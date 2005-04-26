## Script (Python) "hasIndexHtml"
##title=Find out if this folder has an index_html page
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

if not context.isPrincipiaFolderish:
    return False    

if 'index_html' in context.objectIds():
    return True
else:
    return False
    
    