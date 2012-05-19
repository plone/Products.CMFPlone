## Script (Python) "hasAllowedTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return a list of the content types allowed here filtered by getNotAddableTypes

filterOut = context.getNotAddableTypes()
types = context.sortObjects(context.allowedContentTypes())

return [ctype for ctype in types if ctype.getId() not in filterOut]
