## Script (Python) "filterTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=filter
##title=
##
results=[]
try:
    results=filter['portal_type']
except (TypeError,KeyError):
    pass
return results
