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

from Products.CMFPlone import transaction_note
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError
paths=context.REQUEST.get('paths', [])
titles=[]
titles_and_paths=[]
failed = {}
message = ''

MAX_TITLES_TO_REPORT = 10

portal = context.portal_url.getPortalObject()
status='failure'
message='Please select one or more items to delete.'

for path in paths:
    # Skip and note any errors
    try:
        obj = portal.restrictedTraverse(path)
        obj_parent = obj.aq_inner.aq_parent
        obj_parent.manage_delObjects([obj.getId()])
        titles.append(obj.title_or_id())
        titles_and_paths.append('%s (%s)' % (obj.title_or_id(), path))
    except ConflictError:
        raise
    except Exception, e:
        failed[path]= e

if titles:
    status='success'
    if len(titles) == 1:
        message = _(u'${title} has been deleted.',
                    mapping={u'title': titles[0]})
    elif len(titles) <= MAX_TITLES_TO_REPORT:
        message = _(u'${titles} have been deleted.',
                    mapping={u'titles': ', '.join(titles)})
    else:
        message = _(u'${itemCount} items have been deleted.',
                    mapping={u'itemCount': str(len(titles))})

    transaction_note('Deleted %s' % (', '.join(titles_and_paths)))

if failed:
    if message: message = message + '  '
    message = message + "%s could not be deleted."%(', '.join(failed.keys()))

return state.set(status=status, portal_status_message=message)

