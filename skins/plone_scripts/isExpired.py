## Script (Python) "isExpired"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=content
##title=
##
from DateTime import DateTime
from Products.CMFPlone import base_hasattr

if base_hasattr(content, 'expires'):
    try:
        expiry=content.expires()
    except TypeError:
        # expires is not the dublin core 'expires' method
        expiry = None
    if isinstance(expiry, DateTime) and expiry.isPast():
        return 1

return 0

