## Script (Python) "getFolderOrder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None
##title=
##
try:
    return context.aq_parent.objectIds().index(context.getId())
except AttributeError:
    return 0