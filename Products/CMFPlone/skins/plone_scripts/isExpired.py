## Script (Python) "isExpired"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=content=None
##title=Find out if the object is expired
##
from Products.CMFPlone.utils import isExpired
if not content:
    content = context
return isExpired(content)
