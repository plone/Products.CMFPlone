## Controller Python Script "createObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=None,type_name=None,script_id=None
##title=
##

from DateTime import DateTime
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST

if id is None:
    id=context.generateUniqueId(type_name)

# XXX This needs to be moved out of createObject
# its not generic really at all.  
workspaces = 0
if REQUEST.get('type', None) is not None and hasattr(context, 'portal_organization'):
    #We are using Workspaces
    type_name=REQUEST['type']
    workspaces = 1
    state.setStatus('success_workspaces')

if type_name is None:
    raise Exception, 'Type name not specified'

if workspaces or context.portal_factory.getFactoryTypes().has_key(type_name):
    o = context.restrictedTraverse('portal_factory/' + type_name + '/' + id)
    portal_status_message = 'Complete the form to create your ' + type_name + '.'
    transaction_note(o.getTypeInfo().getId() + ' creation initiated.')
else:
    context.invokeFactory(id=id, type_name=type_name)
    o=getattr(context, id, None)
    portal_status_message = type_name + ' has been created.'
    transaction_note(o.getTypeInfo().getId() + ' was created.')

if o is None:
    raise Exception

if o.getTypeInfo().getActionById('edit', None) is None:
    if workspaces:
        state.setStatus('success_workspaces_no_edit')
    else:
        state.setStatus('success_no_edit')

if script_id:
    state.setId(script_id)

return state.set(context=o, portal_status_message=portal_status_message)
