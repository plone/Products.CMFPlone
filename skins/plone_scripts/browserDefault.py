## Script (Python) "browserDefault"
##title=Set Browser Default
##parameters=request

# golly this could be index.html
# return context, ['index.html',]
props = context.portal_properties.site_properties
pages = ['index_html', ]
if props.hasProperty('default_page'):
    pages = props.getProperty('default_page')

if pages:
    # loop through each page given and 
    # return it as the default, if it is found
    # exp = context.aq_explicit
    ids = context.objectIds()
    for page in pages:
        if page in ids:
#        if hasattr(exp, page):
            return context, [page, ]

# what if the page isnt found?
# call the method on the folder, if you
# dont have this you will have problems
# with blank folders
act = context.getTypeInfo().getActionById('view')
if act.startswith('/'):
    act = act[1:]
return context, [act,]
