## Script (Python) "browserDefault"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Set Browser Default
##

# WARNING: Do not remove this, or else WebDAV breaks badly
request = context.REQUEST
if request.has_key('REQUEST_METHOD'):
    if request['REQUEST_METHOD'] not in  ['GET', 'HEAD']:
        return context, [request['REQUEST_METHOD']]

default_pages = ['index_html', ]
pages = getattr(context, 'default_page', [])
props = context.portal_properties.site_properties

# Yeeha. Must be good at logic.
pages = not pages and props.hasProperty('default_page') \
        and props.getProperty('default_page') or pages

# Always look for index_html
pages = pages + default_pages

if pages:
    # loop through each page given and 
    # return it as the default, if it is found
    ids = context.objectIds()
    for page in pages:
        if page in ids:
            return context, [page]

# what if the page isnt found?
try:
    # look for a type action called "folderlisting"
    act = context.getTypeInfo().getActionById('folderlisting')
    if act.startswith('/'):
        act = act[1:]
    return context, [act]
except:
    # if all else fails, fall back to /folder_listing
    return context, ['folder_listing']
