## Script (Python) "isExpired"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=content=None
##title=Find out if the object is expired
##
from DateTime import DateTime
from Products.CMFPlone import base_hasattr

if not content:
    content = context

# NOTE: We also accept catalog brains as 'content' so that the catalog-based
# folder_contents will work. It's a little magic, but it works.

# XXX: It may be better that we use the DC ExpirationDate() accessor, since at
# the moment we're relying on the attribute being available on the object
# explicitly, although this returns an ISO string, not a DateTime object so the 
# code below would have to be modified. AT's contentExpired() method could also 
# be used, but then it wouldn't work with non-AT types.

if base_hasattr(content, 'expires'):
    try:
        expiry=content.expires()
    except AttributeError:
        # DateTime instances are not callable
        # This is an artifact from the past
        
        # NOTE: This will also happen if content is a catalog brain
        expiry=content.expires
    except TypeError:
        # expires is not the dublin core 'expires' method
        expiry = None
    if isinstance(expiry, DateTime) and expiry.isPast():
        return 1

return 0
