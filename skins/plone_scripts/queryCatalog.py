## Script (Python) "queryCatalog"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=show_all=0
##title=wraps the portal_catalog with a rules qualified query
##
results=[]
REQUEST=context.REQUEST
catalog=context.portal_catalog
indexes=catalog.indexes()
query={}
show_query=show_all

for k, v in REQUEST.items():
    if k in indexes:
        query.update({k:v})
        show_query=1
    elif k.endswith('_usage') or k=='sort_on' or k=='sort_order':
        query.update({k:v})

# doesn't normal call catalog unless some field has been queried
# against. if you want to call the catalog _regardless_ of whether
# any items were found, then you can pass show_all=1.

if show_query:
    results=catalog(query)

return results
