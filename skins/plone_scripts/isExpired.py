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
expiry=None

if hasattr(content, 'ExpirationDate'):
    expiry=content.ExpirationDate()

try:
    if DateTime(expiry).isPast():
        return 1
except IndexError:
    pass #Could convert value to DateTime

return 0

