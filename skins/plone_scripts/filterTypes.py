## Script (Python) "filterTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=filter
##title=
##
if same_type(filter, {}) and filter.has_key('Type'):
    return filter['Type']
return []
