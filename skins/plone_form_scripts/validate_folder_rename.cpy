## Controller Python Script "validate_folder_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validate folder renaming
##
state = context.portal_form_controller.getState(script, is_validator=1)

REQUEST=context.REQUEST

old_ids=REQUEST.get('ids',None)
new_ids=REQUEST.get('new_ids',None)
new_titles=REQUEST.get('new_titles',None)

if not new_ids or not old_ids or not new_titles:
    return state.set(status='failure', portal_status_message='Please check an item or items to rename.')

x=0
for id in new_ids:
    old = old_ids[x]
    x = x + 1

    if not id:
        state.setError(old, 'You must enter a name.')
    elif not context.portal_form.good_id(id):
        # id is bad
        state.setError(old, 'This is not a legal name.')
    else:
        # id is good; make sure we have no id collisions
        if id != old:
#            if getattr(context, id, None):
#                 state.setError(old, 'This name is reserved.')
            if id in context.objectIds():
                state.setError(old, 'This name is already in use.')

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state