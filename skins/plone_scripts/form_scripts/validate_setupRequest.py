## Script (Python) "validate_setupRequest"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=errors
##title=sets up the REQUEST 
##
REQUEST=context.REQUEST

for f in REQUEST.form.keys():
    # this chops the field_ prefix off all of variables
    if f[:6]=='field_':
        REQUEST.set(f[6:], REQUEST[f])

if errors:
    # puts the error dictionary into the REQUEST object
    REQUEST.set('errors', errors)
    REQUEST.set('portal_status_message', 'Please correct the indicated errors.')
    for f in REQUEST.form.keys():
        REQUEST.set(f, REQUEST[f])

