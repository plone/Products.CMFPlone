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

#It is better that we use the DC
#ExpirationDate() accessor in the future - after 2.0

if base_hasattr(content, 'expires'):
    try:
        expiry=content.expires()
    except AttributeError:
        # DateTime instances are not callable
        # This is an artifact from the past
        expiry=content.expires
    except TypeError:
        # expires is not the dublin core 'expires' method
        expiry = None
    if isinstance(expiry, DateTime) and expiry.isPast():
        return 1

return 0
