## Script (Python) "browserDefault"
##title=Set Browser Default
##parameters=request

if request['REQUEST_METHOD'] != 'GET':
    return context, [request['REQUEST_METHOD']]

default_pages = ['index_html', ]
pages = getattr(context, 'default_page', [])
props = context.portal_properties.site_properties

# Yeeha. Must be good at logic.
pages = not pages and props.hasProperty('default_page') \
        and props.getProperty('default_page') or pages or default_pages

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
