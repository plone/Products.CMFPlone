## Script (Python) "generateUniqueId"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##
now=DateTime()
prefix=''
if type_name is not None:
    prefix = type_name.replace(' ', '_')+'.'
return prefix+now.strftime('%Y-%m-%d')+'.'+now.strftime('%M%S')
