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
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable

if not content:
    content = context
expiry = None

# NOTE: We also accept catalog brains as 'content' so that the catalog-based
# folder_contents will work. It's a little magic, but it works.

# ExpirationDate should have an ISO date string, which we need to
# convert to a DateTime

# Try DC accessor first
if base_hasattr(content, 'ExpirationDate'):
    expiry=content.ExpirationDate

# Try the direct way
if not expiry and base_hasattr(content, 'expires'):
    expiry=content.expires

# See if we have a callable
if safe_callable(expiry):
    expiry = expiry()

# Convert to DateTime if necessary, ExpirationDate may return 'None'
if expiry and expiry != 'None' and same_type(expiry, ''):
    expiry = DateTime(expiry)

if same_type(expiry, DateTime()) and expiry.isPast():
        return 1
return 0
