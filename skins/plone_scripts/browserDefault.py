## Script (Python) "browserDefault"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Set Browser Default
##

# WebDAV in Zope is odd it takes the incoming verb eg: PROPFIND
# and then requests that object, for example for: /, with verb PROPFIND
# means acquire PROPFIND from the folder and call it
# its all very odd and WebDAV'y
request = context.REQUEST
if request.has_key('REQUEST_METHOD'):
    if request['REQUEST_METHOD'] not in  ['GET', 'HEAD', 'POST']:
        return context, [request['REQUEST_METHOD']]
# now back to normal

default_pages = ['index_html', ]
pages = getattr(context, 'default_page', [])
props = context.portal_properties.site_properties

# Yeeha. Must be good at logic.
#
# if you have a list property default_page on the folder
# it will use that property to determine the page, this means
# you can override it on a folder basis
pages = not pages and props.hasProperty('default_page') \
        and props.getProperty('default_page') or pages

# Always look for index_html
pages = list(pages) + default_pages

if pages:
    # loop through each page given and 
    # return it as the default, if it is found
    try:
        # _robert_ I do not know why
        # but Authenticated is sometimes Anonymous and then
        # a private folder bombs with insufficent privileges
        ids = context.objectIds()
    except:
        ids =[]
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
