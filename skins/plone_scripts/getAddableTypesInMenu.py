## Script (Python) "getAddableTypesInMenu"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=allowedTypes
##title=Return a list of the content type ftis filtered by getImmediatelyAddableTypes(), if available.

try:
    # Find this by acquisition - classes may wish to implement it themselves
    # without all of ConstrainTypesMixin, and they may wish to 
    immediateIds = context.getImmediatelyAddableTypes()
    return [ctype for ctype in allowedTypes if ctype.getId() in immediateIds]
except AttributeError:
    # If we don't have the immediately addable types, fall back on all types
    return allowedTypes
