## Controller Python Script "validate_folder_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids=[],new_ids=[],new_titles=[]
##title=Validate folder renaming
##

ids=[id for id in ids if id]
new_ids=[id for id in new_ids if id]
new_titles=[title for title in new_titles]

if len(ids)!=len(new_ids):
    return state.set(status='failure', portal_status_message='You must provide content names')
if not ids:
    return state.set(status='failure', portal_status_message='Need source content ids.')
if not new_ids:
    state.setError(id, 'Please provide an id')
    return state.set(status='failure', portal_status_message='Need destination content ids.')

check_id=context.check_id
for x in range(0, len(new_ids)):
    id = ids[x]
    newid = new_ids[x]

    if not id:
        state.setError(id, 'You must enter a name.', 'input_required')
        continue

    try:
        resp=check_id(newid)
    except: #XXX Upon calling check_id various exceptions can be raised.  catch all exceptions.
        resp='An error occurred validating new id'

    if resp is not None:
        return state.set(status='failure', portal_status_message=resp)

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
return state
