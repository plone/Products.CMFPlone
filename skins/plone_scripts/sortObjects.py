## Script (Python) "sortObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contents, method='title_or_id'
##title=sorts and pre-filters objects
##

contents=list(contents)
sort = lambda a,b: cmp(getattr(a, method)(), getattr(b, method)())
contents.sort(sort)
return contents
