## Controller Python Script "folder_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##

from Products.CMFPlone import PloneMessageFactory as _

req = context.REQUEST
paths=req.get('paths', [])

putils = context.plone_utils

status='failure'
message=_(u'Please select one or more items to delete.')

success, failure = putils.deleteObjectsByPaths(paths, REQUEST=req)

if success:
    status='success'
    message = _(u'Item(s) deleted.')

if failure:
    message = _(u'${items} could not be deleted.',
                mapping={u'items' : ', '.join(failure.keys())})

context.plone_utils.addPortalMessage(message)
return state.set(status=status)
