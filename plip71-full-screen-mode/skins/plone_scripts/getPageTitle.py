## Script (Python) "getPageTitle"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj, template, portal_title
##title=
##

title = obj.title_or_id()
if title == portal_title or title == obj.getId():
    return template.title_or_id()
return title
