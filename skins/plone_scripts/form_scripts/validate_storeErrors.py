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
if errors:
    REQUEST.set('errors', errors)
    REQUEST.set('portal_status_message', 'Please correct the indicated errors.')
    for f in REQUEST.form.keys():
        REQUEST.set(f, REQUEST[f])

