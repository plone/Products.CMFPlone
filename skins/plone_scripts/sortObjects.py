## Script (Python) "sortObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contents
##title=sorts and pre-filters objects
##

contents=list(contents)
contents.sort(lambda x, y: cmp(x.title_or_id().lower(),y.title_or_id().lower()))
values=contents[:]
del(contents)
return values
