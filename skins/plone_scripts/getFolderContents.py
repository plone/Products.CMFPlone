## Script (Python) "getFolderContents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
if req.has_key('filterString'):
    filter=req['filterString']
    return context.objectValues(list[filter])

return context.objectValues()
