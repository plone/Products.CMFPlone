## Script (Python) "sort_modified_ascending"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=catalog_sequence
##title=
##
sorted = catalog_sequence[:]
sorted.sort(lambda x, y: cmp(x.modified(), y.modified()))
return sorted
