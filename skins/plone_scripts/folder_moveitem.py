## Script (Python) "folder_setorder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=item_id,delta
##title=
##
delta = int(delta)

context.moveObjectsByDelta(item_id, delta)

context.plone_utils.reindexOnReorder(context)

return "<done />"