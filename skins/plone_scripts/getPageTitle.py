## Script (Python) "getPageTitle"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj, template, portal_title
##title=
##

# XXX: Remove in 2.2.
from zLOG import LOG, WARNING
LOG('Plone Debug', WARNING, 'The getPageTitle script is deprecated.  It will '
    'be removed in Plone 2.2')
return obj.title_or_id()
