## Script (Python) "validate_folder_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validate folder renaming
##

REQUEST=context.REQUEST
errors = {}

old_ids=REQUEST.get('ids',None)
new_ids=REQUEST.get('new_ids',None)
new_titles=REQUEST.get('new_titles',None)

if not new_ids or not old_ids or not new_titles:
    return ('failure', errors, {'portal_status_message':'Please check an item or items to rename.'})

x=0
for id in new_ids:
    old = old_ids[x]
    x = x + 1

    if not id:
        errors[old] = 'You must enter a name.'
    elif not context.portal_form.good_id(id):
        # id is bad
        errors[old] = 'This is not a legal name.'
    else:
        # id is good; make sure we have no id collisions
        if id != old:
#            if getattr(context, id, None):
#                errors[old] = 'This name is reserved.'
            if id in context.objectIds():
                errors[old] = 'This name is already in use.'

if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})

return ('success', {}, {})