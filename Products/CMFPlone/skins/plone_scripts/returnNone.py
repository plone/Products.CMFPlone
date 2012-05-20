## Script (Python) "returnNone"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=*args,**kw
##title=Return None

# a simple script to give back 'None'. Useful to masqurade as some other method
# that doesn't really exist, but must be callable.
return None
