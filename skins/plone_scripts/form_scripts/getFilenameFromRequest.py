## Script (Python) "getFilenameFromRequest"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=key
##title=
##
context.plone_debug('inside getFilename')

file=context.REQUEST.get(key, '')
if file:
    context.plone_debug(file.filename)
    return file.filename

return ''

