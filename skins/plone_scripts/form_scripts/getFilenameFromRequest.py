## Script (Python) "getFilenameFromRequest"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=key
##title=
##
file=context.REQUEST.get(key, '')
if file:
    return file.filename
return ''
