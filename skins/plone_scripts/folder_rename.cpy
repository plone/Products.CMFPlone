## Controller Python Script "folder_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=paths=[],new_ids=[],new_titles=[]
##title=Rename Objects
##

from Products.CMFPlone import transaction_note
from ZODB.POSException import ConflictError

portal = context.portal_url.getPortalObject()
failed = {}
success = {}

for x in range(0, len(new_ids)):
    new_id = new_ids[x]
    path = paths[x]
    new_title = new_titles[x]
    obj = portal.restrictedTraverse(path)
    id = obj.getId()
    try:
        if new_title and obj.Title() != new_title:
            obj.setTitle(new_title)
            success[path]=(new_id,new_title)
        if new_id and id != new_id:
            parent = obj.aq_inner.aq_parent
            parent.manage_renameObjects((id,), (new_id,))
            success[path]=(new_id,new_title)
        else:
            obj.reindexObject()
    except ConflictError:
        raise
    except Exception,e:
        failed[path]=e

message = '%s Item(s) renamed.' % str(len(success))
if failed:
    message = message + '  The following item(s) could not be renamed: %s' % ', '.join(failed.keys())
transaction_note('Renamed %s' % str(success.keys))
return state.set(portal_status_message=message)
