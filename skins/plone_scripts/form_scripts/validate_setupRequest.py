## Script (Python) "validate_setupRequest"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=errors
##title=sets up the REQUEST 
##
context.validate_stripPrefixes()
context.validate_storeErrors(errors)
