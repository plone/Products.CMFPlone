## Script (Python) "filterTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=filter
##title=
##
if same_type(filter, {}) and filter.has_key('portal_type'):
    return filter['portal_type']
return []
