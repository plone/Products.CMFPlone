## Script (Python) "validate_storeErrors"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=errors
##title=sets up the REQUEST 
##
REQUEST=context.REQUEST
debug=context.plone_debug
if not same_type(errors ,{}):
    errors={}

id = REQUEST.get('field_id')
if context.getId()!=id:
    if id in context.getParentNode().objectIds():
        errors.update( {'id':'This id already exists.'} )

if errors:
    REQUEST.set('errors', errors)
    REQUEST.set('portal_status_message', 'Please correct the indicated errors.')
    for f in REQUEST.form.keys():
        REQUEST.set(f, REQUEST[f])

