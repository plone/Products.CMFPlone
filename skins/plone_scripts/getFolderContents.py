## Script (Python) "getFolderContents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contentFilter=None
##title=wrapper method around to use catalog to get folder contents
##

catalog = context.portal_catalog.aq_inner
cur_path = '/'.join(context.getPhysicalPath())
path = {}

if not contentFilter:
    contentFilter=context.REQUEST

if not contentFilter.get('sort_on', None):
    try:
        contentFilter.set('sort_on', 'getObjPositionInParent')
    except AttributeError:
        contentFilter['sort_on'] = 'getObjPositionInParent'
    
path['query'] = cur_path
path['depth'] = 1
try:
    contentFilter.set('path', path)
except AttributeError:
    contentFilter['path'] = path

contents = catalog.queryCatalog(contentFilter, show_all=1)

return contents