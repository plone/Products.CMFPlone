## Script (Python) "validate_id"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None
##title=Validates an object id
##

# do basic id validation
errors = context.REQUEST.get('errors', {})
if id is not None:
    id = id.strip()  # PloneTool.contentEdit strips the id, so make sure we test the stripped version
id_error = context.check_id(id, 0, None)
if id_error:
    errors['id'] = id_error
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
else:
    return ('success', errors, {})
