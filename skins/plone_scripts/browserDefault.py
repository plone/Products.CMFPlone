## Script (Python) "browserDefault"
##title=Set Browser Default
##parameters=request

# golly this could be index.html
# return context, ['index.html',]
page = 'index_html'
if page in context.objectIds():
    return context, [page, ]

# what if the page isnt found?
# call the method on the folder, if you
# dont have this you will have problems
# with blank folders
return context, ['view',]
