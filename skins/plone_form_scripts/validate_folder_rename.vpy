## Controller Python Script "validate_folder_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=paths=[],new_ids=[],new_titles=[]
##title=Validate folder renaming
##

paths=[path for path in paths if path]
new_ids=[id for id in new_ids if id]
new_titles=[title for title in new_titles]
portal = context.portal_url.getPortalObject()
check_id = context.check_id

if len(paths)!=len(new_ids):
    return state.set(status='failure',
                     portal_status_message='You must provide content names')

if not paths:
    return state.set(status='failure',
                     portal_status_message='Need source content ids.')

if not new_ids:
    state.setError(id, 'Please provide an id')
    return state.set(status='failure',
                     portal_status_message='Need destination content ids.')

for x in range(0, len(new_ids)):
    path = paths[x]
    newid = new_ids[x]
    obj = portal.restrictedTraverse(path)
    parent = obj.aq_inner.aq_parent
    id = obj.getId()

    if id != newid:
        error = check_id(newid,required=True,contained_by=parent)
        if error:
            state.setError(id, error)


if state.getErrors():
    return state.set(status='failure',
                     portal_status_message='Please correct the indicated errors.')

return state
