## Script (Python) "isExpired"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj
##title=
##
#only if an expirationDate is explicitly Past will this return true

from DateTime import DateTime

try:
    if DateTime(obj.ExpirationDate()).isPast():
        return 1
except: pass

return 0
