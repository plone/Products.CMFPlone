## Script (Python) "getObjSize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None,type_name=None,script_id=None
##title=
##
from DateTime import DateTime
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST

if type_name is None:
    raise Exception

now=DateTime()
if id is None:
	id=type_name.replace(' ', '_')+'.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%M%S')

context.invokeFactory(id=id, type_name=type_name)
o=getattr(context, id, None)

if o is None:
    raise Exception

transaction_note(o.getTypeInfo().getId() + ' was created.')
status = 'success'
try:
    edit_action = o.getTypeInfo().getActionById('edit')
except TypeError:
    status = 'success_no_edit'

script_id = script_id or script.getId()
return context.portal_navigation.getNext(o, script_id, status,
                                         portal_status_message = type_name + ' has been created.')
