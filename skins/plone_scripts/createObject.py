## Script (Python) "getObjSize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None,type_name=None
##title=
##
from DateTime import DateTime
REQUEST=context.REQUEST

if type_name is None:
    raise Exception

if id is None:
	id=type_name.replace(' ', '_')+','+DateTime().strftime('%Y-%m-%d')+','+str(context.random_number())

context.invokeFactory(id=id, type_name=type_name)
o=getattr(context, id, None)

if o is None:
    raise Exception

view=''
try:
    view=o.getTypeInfo().getActionById('edit')
except:
    view=o.getTypeInfo().getActionById('view')

return REQUEST.RESPONSE.redirect(o.absolute_url()+'/'+view)

