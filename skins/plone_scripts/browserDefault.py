## Script (Python) "browserDefault"
##title=Set Browser Default
##parameters=request

if request['REQUEST_METHOD'] != 'GET':
    return context, [request['REQUEST_METHOD']]

props = context.portal_properties.site_properties
pages = ['index_html', ]
if props.hasProperty('default_page'):
    pages = props.getProperty('default_page')

if pages:
    # loop through each page given and 
    # return it as the default, if it is found
    ids = context.objectIds()
    for page in pages:
        if page in ids:
            return context, [page]

# what if the page isnt found?
# call the method on the folder, if you
# dont have this you will have problems
# with blank folders
act = context.getTypeInfo().getActionById('folderlisting')
if act.startswith('/'):
    act = act[1:]
return context, [act]
