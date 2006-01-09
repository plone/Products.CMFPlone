## Script (Python) "getPageTitle"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj, template, portal_title
##title=
##
from Products.CMFPlone.utils import log_deprecated
# BBB: Remove in 2.5.
log_deprecated('The getPageTitle script is deprecated and will '
               'be removed in Plone 2.5.')
return obj.title_or_id()
