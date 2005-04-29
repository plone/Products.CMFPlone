## Script (Python) "sortObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contents, method='title_or_id'
##title=sorts and pre-filters objects
##

aux = [(getattr(o, method)(), o) for o in contents]
aux.sort()
return [x for k, x in aux]
