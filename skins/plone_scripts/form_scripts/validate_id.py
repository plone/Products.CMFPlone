## Script (Python) "validate_id"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None
##title=Validates a link edit_form contents
##

# do basic id validation
errors = context.REQUEST.get('errors', {})
if id:
    if not context.portal_form.good_id(id):
        # id is bad
        errors['id'] = 'This is not a legal id.'
    else:
        # id is good; make sure we have no id collisions

        if not context.getId() in context.getParentNode().objectIds():
            # always check for collisions if we are creating a new object
            checkForCollision = 1
        else:
            # if we have an existing object, only check for collisions if we are changing the id
            checkForCollision = (context.getId() != id)

        # perform the actual check
        if checkForCollision:
            container = context.getParentNode()
            if id in container.objectIds():
                errors[self.id_key] = 'This id already exists.'

if errors:
    return ('failure', errors, {'portal_status_message':'Please correct the indicated errors.'})
else:
    return ('success', errors, {})
