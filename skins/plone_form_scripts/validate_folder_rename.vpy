## Controller Python Script "validate_folder_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=new_ids=[],old_ids=[],new_titles=[]
##title=Validate folder renaming
##

if not new_ids or not old_ids or not new_titles:
    return state.set(status='failure', portal_status_message='Please check an item or items to rename.')

check_id=context.check_id
for x in range(0, len(new_ids)):
    oldid = old_ids[x]
    newid = new_ids[x]

    if not oldid:
        state.setError(oldid, 'You must enter a name.', 'input_required')
        continue

    resp=check_id(newid)
    if resp is not None:
        state.setError(newid, resp)

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state
