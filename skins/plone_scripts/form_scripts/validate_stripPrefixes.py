## Script (Python) "validate_stripPrefixes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=sets up the REQUEST 
##
REQUEST=context.REQUEST

for f in REQUEST.form.keys():
    if f.startswith('field_'):
        REQUEST.set(f[6:], REQUEST[f])
