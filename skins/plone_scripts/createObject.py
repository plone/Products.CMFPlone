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

id=context.generateUniqueId(type_name)

# XXX This needs to be moved out of createObject
# its not generic really at all.  Basically
# in Plone we will be moving to gdavis's CMFFormController
if REQUEST.get('type', None) is not None and \
  hasattr(context, 'portal_organization'):
    #We are using Workspaces
    type_name=REQUEST['type']
    typeinfo=context.portal_types[type_name]
    url='%s/portal_factory/%s/%s/%s' % (context.absolute_url(),
                                        type_name,
                                        id,
                                        typeinfo.getActionById('edit')
                                        )
    return REQUEST.RESPONSE.redirect(url)
    
if type_name is None:
    raise Exception, 'Type name not specified'

if type_name in context.portal_properties.site_properties.portal_factory_types:
    o = context.restrictedTraverse('portal_factory/' + type_name + '/' + id)
else:
    context.invokeFactory(id=id, type_name=type_name)
    o=getattr(context, id, None)

if o is None:
    raise Exception

transaction_note(o.getTypeInfo().getId() + ' was created.')
status = 'success'

if o.getTypeInfo().getActionById('edit', None) is None:
    status='success_no_edit'

script_id = script_id or script.getId()

return context.portal_navigation.getNext(o, 
                                         script_id, 
                                         status,
                                         portal_status_message = type_name + ' has been created.')

