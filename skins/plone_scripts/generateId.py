## Script (Python) "generateId"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None
##title=
##
from DateTime import DateTime
now=DateTime()
type_name=context.getTypeInfo().Title()
if id is None:
	id=type_name.replace(' ', '_')+'.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%M%S')
return id

