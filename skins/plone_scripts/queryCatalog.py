## Script (Python) "queryCatalog"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=wraps the portal_catalog with a rules qualified query
##
results=[]
REQUEST=context.REQUEST
catalog=context.portal_catalog
indexes=catalog.indexes()
query={}

for i in indexes:
    v=REQUEST.get(i, None)
    if v:
        query.update({i:v})

notRawIndexFields=[k for k in REQUEST.form.keys() if k not in query.keys()]
if notRawIndexFields:
    for k in notRawIndexFields:
        if k.endswith('_usage'): 
            query.update({k:REQUEST.get(k)})

if query:
    results=catalog(query)

return results
