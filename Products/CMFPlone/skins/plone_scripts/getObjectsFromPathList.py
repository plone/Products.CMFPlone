## Script (Python) "getObjectsFromPathList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=paths=[],batch=False,b_size=100
##title=method to turn a list of paths into a list of objects
##
from zExceptions import Forbidden
if container.REQUEST.get('PUBLISHED') is script:
   raise Forbidden('Script may not be published.')

contents = []
portal = context.portal_url.getPortalObject()
for path in paths:
    obj = portal.restrictedTraverse(str(path), None)
    if obj is not None: contents.append(obj)

if batch:
    from Products.CMFPlone import Batch
    b_start = context.REQUEST.get('b_start', 0)
    batch = Batch(contents, b_size, int(b_start), orphan=0)
    return batch

return contents
